function getCookieValue(request, cookieName) {
    // console.log('Entering getCookieValue function');
    // console.log('Searching for cookie: ' + cookieName);
    
    if (request.cookies && request.cookies[cookieName] && request.cookies[cookieName].value) {
        const cookieValue = request.cookies[cookieName].value;
        // console.log('Found cookie value: ' + cookieValue);
        return cookieValue;
    } else {
        // console.log('Cookie not found');
        return '';
    }
}

function isValidVersion(version) {
    // console.log('Validating version: ' + version);
    // 修改正则表达式以匹配 v 开头的版本号，允许更多的数字组合
    const isValid = /^v\d+(\.\d+)*$/.test(version);
    // console.log('Is valid version: ' + isValid);
    return isValid;
}

async function handler(event) {
    // console.log('Entering handler function');
    // console.log('Event: ' + JSON.stringify(event));

    var request = event.request;
    var uri = request.uri;

    // console.log('Original URI: ' + uri);

    // 1. 获取版本号
    var version = getCookieValue(request, 'X-Flighthub2-Version');
    // console.log('Retrieved version: ' + version);

    if (!version || !isValidVersion(version)) {
        console.log('Version is invalid or empty, setting to empty string');
        version = '';
    }

    // 2. 路由逻辑
    if (version !== '') {
        // console.log('Processing with version: ' + version);
        if (/^\/multi-stream\/(.*)/.test(uri)) {
            request.uri = '/' + version + '/live-app/index.html';
        } else if (/^\/share\/analysis\/(.*)/.test(uri)) {
            request.uri = '/' + version + '/aec-app/index.html';
        } else if (/^\/share\/(.*)/.test(uri)) {
            request.uri = '/' + version + '/share-resources-app/index.html';
        } else if (/^\/analysis\/(.*)/.test(uri)) {
            request.uri = '/' + version + '/aec-app/index.html';
        } else if (/(?:\/|^)[^./]*$/.test(uri)) {
            request.uri = '/' + version + '/index.html';
        } else {
            request.uri = '/' + version + uri;
        }
    } else {
        // console.log('Processing without version');
        if (/^\/multi-stream\/(.*)/.test(uri)) {
            request.uri = '/live-app/index.html';
        } else if (/^\/share\/analysis\/(.*)/.test(uri)) {
            request.uri = '/aec-app/index.html';
        } else if (/^\/share\/(.*)/.test(uri)) {
            request.uri = '/share-resources-app/index.html';
        } else if (/^\/analysis\/(.*)/.test(uri)) {
            request.uri = '/aec-app/index.html';
        } else if (/(?:\/|^)[^./]*$/.test(uri)) {
            request.uri = '/index.html';
        }
    }

    // console.log('Final URI: ' + request.uri);
    return request;
}