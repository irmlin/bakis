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
  const [username, setUsername] = useState("");

  const handleSetAllowed = (value) => {
    if(!value)
      setAllowed(false);
    else if (value === "true")
      setAllowed(true);
    else
      setAllowed(false);
  }

  const handleSetUsername = (value) => {
    if(!value)
      setUsername("guest");
    else
      setUsername(value);
  }

  useEffect(() => {
    handleSetAllowed(localStorage.getItem("admin"));
    handleSetUsername(localStorage.getItem("username"));
  }, [])

  return <AuthorizationContext.Provider value={[username, allowed]}>{children}</AuthorizationContext.Provider>;
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




  // useEffect(() => {
  //   const fetchUser = async () => {
  //     const response = await getUser();
  //     if (response) {
  //       if (response.status === 200) {
  //         console.log(response);
  //         setUsername(response.data.username);
  //         setAllowed(true);
  //       } else {
  //         console.log("Session expired, please login!");
  //       }
  //     } else {
  //       console.log("No response from the server while fetching user information!");
  //     }
  //   }
  //
  //   fetchUser().then(() => {})
  // }, [])