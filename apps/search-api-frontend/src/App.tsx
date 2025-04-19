import { AppProvider } from "./providers/AppProvider";
import { AppRoutes } from "./routes/routes";
import "./styles/App.css";

function App() {
    return (
        <AppProvider>
            <AppRoutes />
        </AppProvider>
    );
}

export default App;
