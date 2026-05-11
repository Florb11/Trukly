import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import LoginPage from "./pages/LoginPage";
import RegistroPage from "./pages/RegistroPage";


function App() {
  return (
    <BrowserRouter>
      <Navbar />

      <main>
        <Routes>
          <Route path="/" element={<LoginPage />} />  
          <Route path="/registro" element={<RegistroPage />} />   
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default App;
