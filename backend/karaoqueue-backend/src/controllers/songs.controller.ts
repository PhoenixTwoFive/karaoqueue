import { Get, QueryParam, JsonController, Put } from "routing-controllers";

@JsonController("/songs")
export class SongController {
    @Get()
    searchSongs(@QueryParam("query") query: string, @QueryParam("limit") limit: number) {
        return {result: "//TODO search"}
    }

    @Put()
    updateSongs() {
        return "//TODO update"
    }
}