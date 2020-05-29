import { Controller, Get, Res, Post, Delete, Patch, Req } from "routing-controllers";


@Controller("/queue")
export class QueueController {

    /*
     * Fetch entry Queue content
     */
    @Get()
    getQueue(@Req() req: any, @Res() res: any) {
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({ placeholder: "//TODO fetch" }));
    }

    /*
     * Add entry to Queue
     */
    @Post()
    addEntry(@Req() req: any, @Res() res: any) {
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({ placeholder: "//TODO add" }));
    }

    /*
     *
     */
    @Delete()
    clearQueue(@Req() req: any, @Res() res: any) {
        return "//TODO clear";
    }

    /*
     *
     */
    @Get("/:entry:id")
    getEntry(@Req() req: any, @Res() res: any) {
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({ placeholder: "//TODO get" }));
    }

    /*
     *
     */
    @Patch("/:entry_id")
    editEntry(@Req() req: any, @Res() res: any) {
        return "//TODO edit"
    }

    @Delete("/:entry_id")
    deleteEntry(@Req() req: any, @Res() res: any) {
        return "//TODO delete"
    }
}