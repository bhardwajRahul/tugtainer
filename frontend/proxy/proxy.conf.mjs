export default [
  {
    context: ['/api'],
    target: 'http://localhost:8000',
    secure: false,
    logLevel: 'debug',
    changeOrigin: true,
  },
  {
    context: ['/ws'],
    target: 'http://localhost:8000',
    secure: false,
    ws: true,
    logLevel: 'debug',
    changeOrigin: true,
  },
];
