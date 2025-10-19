/**
 * Shared code between client and server
 * Useful to share types between client and server
 * and/or small pure JS functions that can be used on both client and server
 */

/**
 * Example response type for /api/demo
 */
export interface UploadResponse {
  message: string;
  originalname: string;
  filename: string;
  mimetype: string;
  size: number;
  path: string;
}