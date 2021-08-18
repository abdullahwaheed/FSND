/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'abdullah-udacity-fsnd.us',
    audience: 'coffee', // the audience set for the auth0 app
    clientId: 'nN3IWykFm1nnBZ0sZ3JW7TjVlfDRY4oe',
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application. 
  }
};
