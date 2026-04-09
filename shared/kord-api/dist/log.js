export function log(event, data = {}) {
    process.stdout.write(`${JSON.stringify({ event, timestamp: new Date().toISOString(), ...data })}\n`);
}
