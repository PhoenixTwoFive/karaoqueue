import { Request, Response } from "express";
import { Controller, Get, Res, Post, Delete, Patch, Req, Authorized, CurrentUser } from "routing-controllers";
import appState from "../containers/appState.container";
import DataStoredInToken from "../interfaces/dataStoredInToken.interface";


@Controller("/queue")
export class QueueController {

    /*
     * Fetch entry Queue content
     */
    @Get()
    getQueue(@Req() req: Request, @Res() res: Response) {
        res.setHeader('Content-Type', 'application/json');
        res.send(JSON.stringify({ placeholder: "//TODO fetch" }));
        return res;
    }

    /*
     * Add entry to Queue
     */
    @Post()
    addEntry(@Req() req: Request, @Res() res: Response) {
        res.setHeader('Content-Type', 'application/json');
        if (appState.registrationEnabled) {
            res.send(JSON.stringify({ placeholder: "//TODO add" }));
        } else {
            res.status(403)
            res.send("Entry submission is currently not allowed.")
        }
        return res;
    }

    /*
     *
     */
    @Delete()
    @Authorized()
    clearQueue(@Req() req: Request, @Res() res: Response) {
        return "//TODO clear";
    }

    /*
     *
     */
    @Get("/:entry:id")
    getEntry(@Req() req: Request, @Res() res: Response) {
        res.setHeader('Content-Type', 'application/json');
        res.send(JSON.stringify({ placeholder: "//TODO get" }));
        return res;
    }

    /*
     *
     */
    @Patch("/:entry_id")
    editEntry(@Req() req: Request, @Res() res: Response, @CurrentUser() user?: DataStoredInToken) {
        if (user) {
            return "You're "+user._id;
        } else {
            /*TODO: Require song-specific auth to modify queue entry */
            return "You are not logged in."
        }
    }

    @Delete("/:entry_id")
    deleteEntry(@Req() req: Request, @Res() res: Response, @CurrentUser() user?: DataStoredInToken) {
        if (user) {
            return "You're " + user._id;
        } else {
            /*TODO: Require song-specific auth to delete queue entry */
            return "You are not logged in."
        }
    }
}