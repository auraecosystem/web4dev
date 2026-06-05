mkdir myproj ; cd myproj
npx -y firebase-tools@latest login --reauth
npx -y firebase-tools@latest init dataconnect
npx -y firebase-tools@latest deploy --only dataconnect
npx -y firebase-tools@latest \
         dataconnect:execute dataconnect/seed_data.gql
         npx -y firebase-tools@latest dataconnect:sdk:generate

npx -y firebase-tools@latest \
          apps:create web react-example
npx -y firebase-tools@latest \
          apps:sdkconfig web \
          -o web-app/src/firebase-config.json
cd web-app
npm i firebase \
            @tanstack/react-query \
            @tanstack-query-firebase/react
