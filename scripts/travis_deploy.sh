#!/bin/bash

set -x
if [ $TRAVIS_BRANCH == 'master' ] ; then
    eval "$(ssh-agent -s)"
    chmod 600 ./deploy_key
    ssh-add ./deploy_key

    git init

    git remote add deploy "$SERVER_USER@$SERVER_ADDRESS:$GIT_PATH"
    git config user.name "Travis CI"
    git config user.email "$DEPLOY_EMAIL"

    git add .
    git commit -m "Deploy"
    git push --force deploy master -v

    chmod 600 deploy_key
    ssh -o StrictHostKeyChecking=no -i ./deploy_key $SERVER_USER@$SERVER_ADDRESS "$REPOPATH/scripts/deploy.sh"
else
    echo "Not deploying, since this branch isn't master."
fi