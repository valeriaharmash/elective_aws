#####################################################
##                 CHECKS                          ##
####################################################
check-project-var:
	@[ "${PROJECT}" ] || ( echo "Variable [PROJECT] is not set"; exit 1 )

check-stack-var:
	@[ "${STACK}" ] || ( echo "Variable [STACK] is not set"; exit 1 )

check-env-var:
	@[ "${ENV}" ] || ( echo "Variable [ENV] is not set"; exit 1 )

check-region-var:
	@[ "${REGION}" ] || ( echo "Variable [REGION] is not set"; exit 1 )
	$(eval REGION_SHORTCUT_1 := $(shell echo ${REGION}| cut -d "-" -f 1 ))
	$(eval REGION_SHORTCUT_2 := $(shell echo ${REGION}| cut -d "-" -f 2 | cut -c1-1))
	$(eval REGION_SHORTCUT_3 := $(shell echo ${REGION}| cut -d "-" -f 3 ))
	$(eval REGION_SHORTCUT := $(shell echo ${REGION_SHORTCUT_1}${REGION_SHORTCUT_2}${REGION_SHORTCUT_3} ))
	@echo 'Region shortcut is [${REGION_SHORTCUT}]'

check-application-var:
	@[ "${APPLICATION}" ] || ( echo "Variable [APPLICATION] is not set"; exit 1 )

check-required-properties: check-project-var
	$(eval S3_PATH := $(shell aws cloudformation describe-stacks --stack-name ${PROJECT}-s3 --query "Stacks[0].Outputs[?OutputKey=='S3Bucket'].OutputValue" --output text))
	$(eval S3_BUCKET_NAME := $(shell aws cloudformation describe-stacks --stack-name ${PROJECT}-s3 --query "Stacks[0].Outputs[?OutputKey=='S3BucketName'].OutputValue" --output text))
#	$(eval MACROS_ID := $(shell aws cloudformation describe-stacks --stack-name ${STACK}-macros --query "Stacks[0].StackId" --output text))
	$(eval ACCOUNT_ID := $(shell aws sts get-caller-identity --query "Account" --output text))
	@[ "${S3_PATH}" ] || ( echo "S3 path is not set"; exit 1 )
	@[ "${ACCOUNT_ID}" ] || ( echo "Account is not set"; exit 1 )
#	@[ "${MACROS_ID}" ] || ( echo "Macros is not set"; exit 1 )
	@echo 'All required properties are set'

install:
	@echo 'boto3, pyyaml, awscli, aws-sam-cli, python3.11 are needed. Please, install them.'
	@echo 'You can use the following commands [MacOS]:'
	@echo 'brew install python@3.11'
	@echo 'pip install aws-sam-cli'
	@echo 'pip install awscli'
	@echo 'pip install pyyaml'
	@echo 'pip install boto3'

#####################################################
##                 SETUP                          ##
####################################################
setup-s3: check-project-var check-env-var check-region-var
	@echo 'Creating s3 work folder for ${PROJECT}...'
	@aws cloudformation deploy --stack-name ${PROJECT}-s3 --region ${REGION} --template-file applications/system/s3.yml --parameter-overrides ProjectName=${PROJECT} ExecEnv=${ENV} RegionName=${REGION} RegionShortcut=${REGION_SHORTCUT} --capabilities CAPABILITY_IAM
	@echo 'S3 work folder for [${PROJECT}] is created'

setup-show-s3: check-project-var
	@echo 'Extracting S3_PATH from cloudformation stack [${PROJECT}-s3]...'
	$(eval S3_PATH := $(shell aws cloudformation describe-stacks --stack-name ${PROJECT}-s3 --query "Stacks[0].Outputs[?OutputKey=='S3Bucket'].OutputValue" --output text))
	$(eval S3_BUCKET_NAME := $(shell aws cloudformation describe-stacks --stack-name ${PROJECT}-s3 --query "Stacks[0].Outputs[?OutputKey=='S3BucketName'].OutputValue" --output text))
	$(eval ACCOUNT_ID := $(shell aws sts get-caller-identity --query "Account" --output text))
	@echo 'Work directory is [${S3_PATH}]'
	@echo 'Account is [${ACCOUNT_ID}]'

setup-stacks: setup-show-s3
	@echo 'Uploading stacks for [${PROJECT}]...'
	@aws s3 sync stacks/ ${S3_PATH}/stacks/ --exclude '*' --include '*.yml' --include '*.json'

setup: setup-s3 setup-stacks check-required-properties

#####################################################
##                 PUBLISH                         ##
####################################################
publish-one-application: check-project-var check-application-var check-required-properties check-region-var setup-show-s3
	@echo 'Uploading application for [${PROJECT}]...'
	$(eval SEMANTIC_VERSION := $(shell grep 'SemanticVersion:' applications/${APPLICATION}/template.yml | cut -d":" -f2- | xargs ))
	@echo '${SEMANTIC_VERSION}'
	@if aws serverlessrepo get-application --application-id arn:aws:serverlessrepo:${REGION}:${ACCOUNT_ID}:applications/${APPLICATION} --semantic-version ${SEMANTIC_VERSION} > /dev/null 2>&1; then echo "Version already exists" && exit 1; fi
	@sam build -t "applications/${APPLICATION}/template.yml"
	@sam package -t .aws-sam/build/template.yaml --s3-bucket ${S3_BUCKET_NAME} --s3-prefix package/${APPLICATION} --output-template-file ${APPLICATION}.temp
	@sam publish --region ${REGION} --template ${APPLICATION}.temp || true
	@aws s3 mv ${APPLICATION}.temp ${S3_PATH}/applications/${SEMANTIC_VERSION}/${APPLICATION}.yml

#####################################################
##                 DEPLOY                         ##
####################################################
deploy-stack: check-project-var check-env-var check-stack-var check-required-properties check-region-var setup-show-s3
	@echo 'Uploading stack ${STACK} for [${PROJECT}] in [${ENV}] environment...'
	@aws s3 sync stacks/${STACK}/ ${S3_PATH}/stacks/${STACK}/ --exclude '*' --include '*.yml' --include '*.json'
	@echo 'Deploying stack [${STACK}] for [${PROJECT}] in [${ENV}] environment...'
	@cp stacks/${STACK}/template.yml temp-${STACK}-${ENV}-template.yml
	@sed -i -e 's/$${AWS::AccountId}/${ACCOUNT_ID}/g' temp-${STACK}-${ENV}-template.yml
	@sed -i -e 's/$${AWS::Region}/${REGION}/g' temp-${STACK}-${ENV}-template.yml
	@sed -i -e 's/$${S3_PATH}/${S3_BUCKET_NAME}/g' temp-${STACK}-${ENV}-template.yml
	@sam build -t temp-${STACK}-${ENV}-template.yml
	$(eval SAM_PARAMS := $(shell [ -f "stacks/${STACK}/params.${ENV}.json" ] && cat stacks/${STACK}/params.${ENV}.json | jq -r '.[] | "\(.ParameterKey)=\(.ParameterValue)"'))
	@echo 'Params are: ${SAM_PARAMS}'
	@sam deploy -t temp-${STACK}-${ENV}-template.yml --stack-name ${PROJECT}-${STACK}-${ENV} --region ${REGION} --no-confirm-changeset --s3-bucket ${S3_BUCKET_NAME} --s3-prefix stacks/${STACK}/sam --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM --parameter-overrides ProjectName=${PROJECT} StackName=${STACK} S3AppPath=${PROJECT}-setup-s3 ExecEnv=${ENV} RegionName=${REGION} RegionShortcut=${REGION_SHORTCUT}  ${SAM_PARAMS} --tags Team=WcmTango2Team Environment=${ENV} Project=wcm-tango2 Stack=${STACK} Region=${REGION}
	@rm temp-${STACK}-${ENV}-template.yml
	@rm temp-${STACK}-${ENV}-template.yml-e || true
	@echo 'Deployed stack [${STACK}] for [${PROJECT}] in [${ENV}] environment'

delete-stack: check-project-var check-stack-var check-env-var check-region-var
	@aws cloudformation delete-stack --stack-name ${PROJECT}-${STACK}-${ENV} --region ${REGION}
	@echo 'Waiting for stack ${STACK} for [${PROJECT}] in [${ENV}] environment to be deleted...'
	@aws cloudformation wait stack-delete-complete --stack-name ${PROJECT}-${STACK}-${ENV} --region ${REGION}
	@echo 'Stack ${STACK} for [${PROJECT}] in [${ENV}] environment is deleted'
