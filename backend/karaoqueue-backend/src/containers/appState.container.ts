import AppState from "../models/appState.model";
import fs from "fs";

const appState = new AppState();

if (fs.existsSync("/tmp/.kqueue_eventlock")) {
    appState.currentlyInEvent=true;
} else {
    appState.currentlyInEvent=false;
}

appState.registrationEnabled=false;

export default appState;