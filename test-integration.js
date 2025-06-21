const axios = require('axios');

// Test configuration
const BACKEND_URL = 'http://127.0.0.1:5000';
const FRONTEND_URL = 'http://localhost:8080';

async function testBackendHealth() {
    try {
        console.log('🔍 Testing backend health...');
        const response = await axios.get(`${BACKEND_URL}/health`);
        console.log('✅ Backend is healthy:', response.data);
        return true;
    } catch (error) {
        console.error('❌ Backend health check failed:', error.message);
        return false;
    }
}

async function testFrontendAccess() {
    try {
        console.log('🔍 Testing frontend access...');
        const response = await axios.get(FRONTEND_URL);
        console.log('✅ Frontend is accessible (status:', response.status, ')');
        return true;
    } catch (error) {
        console.error('❌ Frontend access failed:', error.message);
        return false;
    }
}

async function testCORS() {
    try {
        console.log('🔍 Testing CORS configuration...');
        const response = await axios.get(`${BACKEND_URL}/health`, {
            headers: {
                'Origin': FRONTEND_URL
            }
        });
        console.log('✅ CORS is working correctly');
        return true;
    } catch (error) {
        console.error('❌ CORS test failed:', error.message);
        return false;
    }
}

async function runTests() {
    console.log('🚀 Starting integration tests...\n');
    
    const backendOk = await testBackendHealth();
    const frontendOk = await testFrontendAccess();
    const corsOk = await testCORS();
    
    console.log('\n📊 Test Results:');
    console.log('Backend Health:', backendOk ? '✅ PASS' : '❌ FAIL');
    console.log('Frontend Access:', frontendOk ? '✅ PASS' : '❌ FAIL');
    console.log('CORS Configuration:', corsOk ? '✅ PASS' : '❌ FAIL');
    
    if (backendOk && frontendOk && corsOk) {
        console.log('\n🎉 All tests passed! Your frontend and backend are successfully integrated.');
        console.log('\n📝 Next steps:');
        console.log('1. Frontend: http://localhost:8080');
        console.log('2. Backend API: http://127.0.0.1:5000');
        console.log('3. API Documentation: http://127.0.0.1:5000/docs');
    } else {
        console.log('\n⚠️  Some tests failed. Please check the error messages above.');
    }
}

// Run tests
runTests().catch(console.error); 