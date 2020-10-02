import { Request, Response } from "express";
import { Post, BodyParam, Body, Res, Req, JsonController, UseBefore, Get, CookieParam } from "routing-controllers";
import User from "../interfaces/user.interface";
import { JwtMiddleware } from "../middleware/jwt.middleware";

@JsonController("/auth")
export class AuthenticationController {

    @Post("/login")
    doLogin(@Body() user: User, @Res() res: Response) {
        if (user.username === process.env.KQUEUE_USERNAME) {
            if (user.password === process.env.KQUEUE_PASSWORD) {
                const jwtMiddleware = new JwtMiddleware();
                const tokenData = jwtMiddleware.createToken(user);
                res.cookie("jwt",tokenData,);
                res.status(200);
                res.send("Welcome.")
                return res;
            } else {
                // TODO wrong password.
                return "Wrong password."
            }
        } else {
            // TODO wrong user.
            return "Wrong user."
        }
    }

    @Get("/logout")
    doLogout() {
        return "//TODO logout";
    }
}