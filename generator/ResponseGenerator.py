from models.Response import Response

class ResponseGenerator:
    @staticmethod
    def generateResponseObject(responseData, position, id):
        if responseData != None:
            status = responseData.status_code
            header = responseData.headers
            body = responseData.text
            time = responseData.elapsed.total_seconds()
            response = Response(status, header, body, time, position, id)
            return response
        else:
            return None