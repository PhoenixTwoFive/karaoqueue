import { Response } from "express";
import { Authorized, Controller, Get, Param, QueryParam, Res } from "routing-controllers";
import appState from "../containers/appState.container";
import fs from "fs";

@Controller("/rpc")
@Authorized()
export class RpcController {
    @Get("/start_event")
    doStartEvent() {
        /* TODO: Wipe state (queue and song playbacks) when starting new event. Maybe also refresh Song database automatically? */
        appState.currentlyInEvent = true;
        fs.openSync("/tmp/.kqueue_eventlock", 'w')
        return 200;
    }

    @Get("/end_event")
    doEndEvent() {
        appState.currentlyInEvent = false;
        fs.unlinkSync("/tmp/.kqueue_eventlock");
        return 200;
    }

    @Get("/enable_registration")
    doEnableRegistration(@Res() res: Response) {
        if (appState.currentlyInEvent) {
            appState.registrationEnabled = true;
            return 200;
        } else {
            res.status(403).send("No event currently active")
            return res;
        }
    }

    @Get("/disable_registration")
    doDisableRegistration(@Res() res: Response) {
        if (appState.currentlyInEvent) {
            appState.registrationEnabled = false;
            return 200;
        } else {
            res.status(403).send("No event currently active")
            return res;
        }

    }

    @Get("/get_state")
    doGetState() {
        return appState;
    }

    @Get("/get_playstats")
    doGetPlaystats() {
        return "//TODO get_playstats"
    }

    @Get("/download_playstats")
    doDownloadPlaystats() {
        return "//TODO download_playstats"
    }

    @Get("/entry_fulfilled")
    doEntryFulfilled(@QueryParam("entry_id") entryId: string) {
        return `//TODO entry_fulfilled. entry_id: ${entryId}`
    }
}