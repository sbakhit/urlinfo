from flask import Flask, request

app = Flask(__name__)

import dynamodb_handler as dynamodb


@app.route('/')
def root_route():
    return {'msg': 'Specify API'}

@app.route('/urlinfo')
def root_route_urlinfo():
    return {'msg': 'Specify API Version'}

@app.route('/urlinfo/1', methods=['POST'])
def create_urlinfo():
    data = request.get_json()
    if not data or not data.get('url') or not data.get('is_safe'):
        return {'msg': 'Missing required data `url` and/or `is_safe`'}, 400

    is_safe = str(data['is_safe']).lower()
    if is_safe != 'true' and is_safe != 'false':
        return {'msg': 'Wrong type for `is_safe`. Must be True/False'}, 400
    is_safe = True if is_safe == 'true' else False

    response = dynamodb.AddItemToURLInfo(data['url'], is_safe)
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        return {
            'msg': 'Some error occured',
            'response': response
        }, 400

    return {'msg': 'Added successfully'}

@app.route('/urlinfo/1/<string:url>', methods=['GET'])
def read_urlinfo(url: str):
    response = dynamodb.GetItemFromURLInfo(url)
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        return {
            'msg': 'Some error occured',
            'response': response
        }, 400

    if 'Item' not in response:
        return {'msg': 'Not Found'}, 404

    return {'Item': response['Item']}, 200

@app.route('/urlinfo/1/<string:url>/safe', methods=['PUT'])
def update_urlinfo_safe(url: str):
    response = dynamodb.UpdateURLSafeFlag(url, is_safe=True)
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        return {
            'msg': 'Some error occured',
            'response' : response
        }, 400

    return {
        'msg': 'Updated successfully',
        'ModifiedAttributes': response['Attributes'],
    }, 200

@app.route('/urlinfo/1/<string:url>/unsafe', methods=['PUT'])
def update_urlinfo_unsafe(url: str):
    response = dynamodb.UpdateURLSafeFlag(url, is_safe=False)
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        return {
            'msg': 'Some error occured',
            'response' : response
        }, 400

    return {
        'msg': 'Updated successfully',
        'ModifiedAttributes': response['Attributes'],
    }, 200

@app.route('/urlinfo/1/<string:url>', methods=['DELETE'])
def delete_urlinfo(url: str):
    response = dynamodb.DeleteAnItemFromURLInfo(url)
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        return {
            'msg': 'Some error occured',
            'response' : response
        }, 400

    return {'msg': 'Deleted successfully'}, 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)

