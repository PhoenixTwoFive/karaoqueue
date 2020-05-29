import { Controller, Get, Param, QueryParam } from "routing-controllers";

@Controller("/rpc")
export class RpcController {
    @Get("/start_event")
    doStartEvent() {
        return "//TODO start_event"
    }

    @Get("/end_event")
    doEndEvent() {
        return "//TODO end_event"
    }

    @Get("/enable_registration")
    doEnableRegistration() {
        return "//TODO enable_registration"
    }

    @Get("/disable_registration")
    doDisableRegistration() {
        return "//TODO disable_registration"
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