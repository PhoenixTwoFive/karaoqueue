import { Get, QueryParam, JsonController, Put, Authorized } from "routing-controllers";


@JsonController("/songs")
export class SongController {
    @Get()
    searchSongs(@QueryParam("query") query: string, @QueryParam("limit") limit: number) {
        return {result: "//TODO search"}
    }

    @Put()
    @Authorized()
    updateSongs() {
        return "//TODO update"
    }
}