import React from "react";
import Chatbot from "./components/Chatbot.js";
import backgroundImage from './components/ExampleMacewanHomepage.jpg'

const App = () => {
  // Add example background image
  const appStyle = {
    backgroundImage: `url(${backgroundImage})`, 
    backgroundSize: "cover", 
    backgroundRepeat: "no-repeat", 
    backgroundPosition: "center", 
    height: "100vh", 
    width: "100vw",
    margin: 0, 
  };

  return (
    <div style={appStyle}>
      <Chatbot />
    </div>
  );
};

export default App;
