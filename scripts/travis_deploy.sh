#!/bin/bash

set -x
if [ $TRAVIS_BRANCH == 'master' ] ; then
    git init

    git remote add deploy "$SERVER_USER@$SERVER_ADDRESS:$GIT_PATH"
    git config user.name "Travis CI"
    git config user.email "$DEPLOY_EMAIL"

    git add .
    git commit -m "Deploy"
    git push --force deploy master -v
else
    echo "Not deploying, since this branch isn't master."
fi