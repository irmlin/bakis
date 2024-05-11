/**
=========================================================
* Material Dashboard 2 React - v2.2.0
=========================================================

* Product Page: https://www.creative-tim.com/product/material-dashboard-react
* Copyright 2023 Creative Tim (https://www.creative-tim.com)

Coded by www.creative-tim.com

 =========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

/**
  This file is used for controlling the global states of the components,
  you can customize the states for the different components here.
*/

import {createContext, useContext, useEffect, useState} from "react";
const AuthorizationContext = createContext();

function AuthorizationContextProvider({ children }) {

  const [allowed, setAllowed] = useState(false);

  useEffect(() => {
    const admin = localStorage.getItem("admin");
    if(!admin)
      setAllowed(false);
    else if (admin === "true")
      setAllowed(true);
    else
      setAllowed(false);
  }, [])

  return <AuthorizationContext.Provider value={[allowed]}>{children}</AuthorizationContext.Provider>;
}

// Material Dashboard 2 React custom hook for using Context
function useAuthorizationContext() {
  const context = useContext(AuthorizationContext);

  if (!context) {
    throw new Error(
      "useAuthorizationContext should be used inside the AuthorizationContextProvider."
    );
  }

  return context;
}

export {
  useAuthorizationContext,
  AuthorizationContextProvider
};
