import "reflect-metadata";
import { Request, Response, Application } from "express";
import { Action, createExpressServer } from "routing-controllers";
import { QueueController } from "./controllers/queue.controller";
import { SongController } from "./controllers/songs.controller";
import { StatisticsController } from "./controllers/statistics.controller";
import { AuthenticationController } from "./controllers/auth.controller";
import { RpcController } from "./controllers/rpc.controller";
import jwt from "jsonwebtoken";
import appState from "./containers/appState.container";


import * as dotenv from "dotenv";
import DataStoredInToken from "./interfaces/dataStoredInToken.interface";
dotenv.config();

const app: Application = createExpressServer({
    routePrefix: "/api",
    cors: true,
    /* HACK. This definitely needs to be cleaned up... */
    authorizationChecker: async (action: Action) => {
        const req: Request = action.request;
        const secret = process.env.KQUEUE_JWTSECRET;
        // tslint:disable-next-line: no-string-literal
        const token = parseCookies(req.headers.cookie)['jwt'];
        if (token) {
            try {
                const verificationResponse = jwt.verify(token, secret);
                if (verificationResponse) {
                    return true;
                } else {
                    return false;
                }
            } catch (error) {
                return false;
            }
        } else {
            return false;
        }
    },
    /* HACK. This definitely needs to be cleaned up... */
    currentUserChecker: async (action: Action) => {
        const req: Request = action.request;
        const secret = process.env.KQUEUE_JWTSECRET;
        // tslint:disable-next-line: no-string-literal
        const token = parseCookies(req.headers.cookie)['jwt'];
        if (token) {
            try {
                const verificationResponse = jwt.verify(token, secret);
                if (verificationResponse) {
                    return verificationResponse as DataStoredInToken;
                } else {
                    return false;
                }
            } catch (error) {
                return false;
            }
        } else {
            return false;
        }
    },
    controllers: [QueueController, SongController, StatisticsController, AuthenticationController, RpcController]
});
app.listen(process.env.KQUEUE_PORT);

/* HACK. This definitely needs to be cleaned up... */
function parseCookies(str) {
    const rx = /([^;=\s]*)=([^;]*)/g;
    const obj = {};
    // tslint:disable-next-line: no-conditional-assignment
    for (let m; m = rx.exec(str);)
        obj[m[1]] = decodeURIComponent(m[2]);
    return obj;
}