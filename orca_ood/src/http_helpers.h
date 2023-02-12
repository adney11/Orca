#ifndef HTTP_HELPERS_
#define HTTP_HELPERS_

#include "common.h"
#include <cstdlib>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/sendfile.h>


#define RESPONSE_HEADER_SIZE 100
const char* HTTP_SERVER_ROOT_PATH = "/newhome/Orca/orca_ood/pensieve/video_server";
const char* http_header = "HTTP/1.1 200 Ok\r\n";


struct HTTPRequestLine {
    char* method;
    char* resource;
    char* http_version;
};

struct HTTPResponse {
        char* headers;
        int fd_to_body;
        struct stat body_stats;
};

struct HTTPResponse* init_HTTPResponse(char* version, int status_code, char* reason_phrase, char* content_type, char* content_path) {
    struct HTTPResponse* response = (struct HTTPResponse*)malloc(sizeof(struct HTTPResponse));
    
    // now body
    if (content_type == NULL) {
        sprintf(response->headers, "%s %d %s\r\n\r\n",
            version, status_code, reason_phrase);
        response->fd_to_body = -1;
        return response;
    }
    DBGMARK(0,0, "trying to open resource at %s\n", content_path);
    response->fd_to_body = open(content_path, O_RDONLY);
    if (response->fd_to_body < 0) {
        DBGMARK(0,0,"can't open resource: %s due to error: %d\n", content_path, response->fd_to_body);
    }
    fstat(response->fd_to_body, &response->body_stats);
    response->headers = (char*)malloc(RESPONSE_HEADER_SIZE);
    sprintf(response->headers, "%s %d %s\r\nContent-Type: %s\r\nContent-Length: %ld\r\n\r\n",
        version, status_code, reason_phrase, content_type, response->body_stats.st_size);
    DBGMARK(0,0, "made new HTTPResponse header:\n--- BEGIN RESPONSE ---\n%s\n----- END RESPONSE ----\n", response->headers);
    return response;
}

void free_HTTPResponse(struct HTTPResponse* response) {
    free(response->headers);
    close(response->fd_to_body);
    free(response);
    DBGMARK(0,0, "freed all memory for HTTPResponse\n");
}

struct HTTPRequestLine* init_HTTPRequestLine(char* method, char* resource, char* version) {
    struct HTTPRequestLine *line = (struct HTTPRequestLine*)malloc(sizeof(struct HTTPRequestLine));
    line->method = (char*)malloc(sizeof(char*));
    strcpy(line->method, method);
    line->resource = (char*)malloc(sizeof(char*));
    strcpy(line->resource, resource);
    line->http_version = (char*)malloc(sizeof(char*));
    strcpy(line->http_version, version);
    return line;
}

void free_HTTPRequestLine(struct HTTPRequestLine* line) {
    free(line->method);
    free(line->resource);
    free(line->http_version);
    free(line);
    DBGMARK(0,0, "cleanedup memory for request line\n");
}

struct HTTPRequestLine* parse_request(char* request, int request_len) {
    char* request_copy = (char*)malloc(request_len + 1);
    strcpy(request_copy, request);

    char* request_line = strtok(request_copy, "\n");
    DBGMARK(0,0, "request line is: %s\n", request_line);
    char* method = strtok(request_line, " ");
    DBGMARK(0,0, "method is: %s\n", method);
    char* resource = strtok(NULL, " ");
    DBGMARK(0,0, "resource is: %s\n", resource);
    char* http_version = strtok(NULL, " ");
    DBGMARK(0,0, "http_version is: %s\n", http_version);

    return init_HTTPRequestLine(method, resource, http_version);
}

int send_data(int sock, void* data, int length) {
    unsigned char *pdata = (unsigned char *) data;
    int sent;

    while (length > 0) {
        sent = send(sock, pdata, length, 0);
        if (sent == -1) return sent;
        pdata += sent;
        length -= sent;
    }
    return 0;
}

int send_response(int sock, HTTPResponse* response) {
    // first send headers
    int sent;
    sent = send_data(sock, response->headers, strlen(response->headers));
    if (sent < 0) {
        DBGMARK(0,0, "failed to send response headers\n");
        return sent;
    } else if (sent == 0){
        DBGMARK(0,0,"sent response header\n");
    }
    // then send body
    if (response->fd_to_body == -1)
        return 0;
    
    int total_body_size = response->body_stats.st_size;
    int block_size = response->body_stats.st_blksize;
    int init_body_size  = total_body_size;
    if (response->fd_to_body >= 0) {
        DBGMARK(0,0,"sending response body\n");
        ssize_t sent;
        while (total_body_size > 0) {
            int bytes_to_send = ((total_body_size < block_size) ? total_body_size : block_size);
            sent = sendfile(sock, response->fd_to_body, NULL, block_size);
            if (sent < 0) {
                DBGMARK(0,0,"failed to send response body - trying again\n");
            } else {
                total_body_size -= sent;
            }
        }
    }
    if (total_body_size != 0) {
        DBGMARK(0,0, "body has leftover %d bytes to send..\n", total_body_size);
    } else {
        // destroy the http response
        free_HTTPResponse(response);
    }
    return 0;
}


char* parse_resource_extension(char* resource_path) {
    char* copy = (char*)malloc(sizeof(resource_path));
    strcpy(copy, resource_path);

    // /index.html
    // /video1/1.m4s
    char* tok = strtok(copy, ".");
    tok = strtok(NULL, ".");
    DBGMARK(0,0,"resource %s has extension %s\n", resource_path, tok);
    return tok;
}

#endif // HTTP_HELPERS_