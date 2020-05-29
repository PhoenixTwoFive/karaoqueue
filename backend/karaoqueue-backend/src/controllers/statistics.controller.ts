import { JsonController, Get } from "routing-controllers";

@JsonController()
export class StatisticsController {
    @Get()
    getStatistics() {
        return "//TODO statistics"
    }
}