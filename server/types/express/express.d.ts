import "express";

declare global {
    interface Request {
        file?: Express.Multer.File;
        files?: Express.Multer.File[];
    }
}