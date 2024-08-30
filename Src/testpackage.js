function getOldTestPackage(message)
{
    const hash = crypto.createHash('sha256');
    hash.update(message);
    const hashedMessage = hash.digest('hex');
    return hashedMessage;
}

async function getTestPackage(message) {
    const encoder = new TextEncoder();
    const data = encoder.encode(message);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashedMessage = hashArray.map(byte => byte.toString(16).padStart(2, '0')).join('');
    return hashedMessage;
}
