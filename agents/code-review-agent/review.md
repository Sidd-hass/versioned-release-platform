# Code Review

## Executive Summary

This repository contains a full-stack application with a Node.js/Express backend and React frontend, deployed via Docker Compose. The codebase is functional but has several security and operational concerns that need attention. The CI/CD pipeline is well-structured for building and releasing versioned Docker images, but lacks automated testing capabilities.

## Critical Issues

None identified.

## High Issues

### F1: Overly Permissive CORS Configuration
- **File**: `backend/server.js`
- **Evidence**: `app.use(cors());`
- **Impact**: Any website can make cross-origin requests to the backend, potentially exposing sensitive data or enabling CSRF attacks
- **Recommendation**: Configure CORS with specific allowed origins instead of using the default permissive settings

### F2: Unauthenticated Health and Version Endpoints
- **File**: `backend/server.js`
- **Evidence**: 
  ```javascript
  app.get("/api/health", (req, res) => {
    res.json({
      status: "healthy",
      version: APP_VERSION
    });
  });
  ```
- **Impact**: Internal system information including version numbers is exposed to external users, which could aid attackers in targeting specific vulnerabilities
- **Recommendation**: Restrict access to health and version endpoints to internal networks or add authentication

## Medium Issues

### F4: Missing JSON Body Size Limits
- **File**: `backend/server.js`
- **Evidence**: `app.use(express.json());`
- **Impact**: Attackers could send extremely large JSON payloads to exhaust server memory and cause denial of service
- **Recommendation**: Configure express.json() with a size limit parameter to prevent memory exhaustion attacks

### F5: Version Information Leakage
- **File**: `backend/server.js`
- **Evidence**: 
  ```javascript
  app.get("/api/version", (req, res) => {
    res.json({
      version: APP_VERSION
    });
  });
  ```
- **Impact**: Version information leakage could help attackers identify known vulnerabilities in specific versions
- **Recommendation**: Remove or restrict access to version endpoints in production environments

## Low / Informational

### F6: Backend Running as Root
- **File**: `backend/Dockerfile`
- **Evidence**: `CMD ["node", "server.js"]`
- **Impact**: The application runs as root inside the container, which increases the potential impact if the container is compromised
- **Recommendation**: Create a non-root user in the Dockerfile and run the application as that user

### F7: Frontend Running as Root
- **File**: `frontend/Dockerfile`
- **Evidence**: `CMD ["nginx", "-g", "daemon off;"]`
- **Impact**: The application runs as root inside the container, which increases the potential impact if the container is compromised
- **Recommendation**: Create a non-root user in the Dockerfile and run the application as that user

### F9: Missing Backend Tests
- **File**: `backend/package.json`
- **Evidence**: `"scripts": { "start": "node server.js", "dev": "nodemon server.js" }`
- **Impact**: There is no automated testing for the backend code, which may lead to undetected bugs and regressions
- **Recommendation**: Add test scripts and a test framework to the backend project

### F10: Missing Frontend Tests
- **File**: `frontend/package.json`
- **Evidence**: `"scripts": { "dev": "vite", "build": "vite build", "lint": "eslint .", "preview": "vite preview" }`
- **Impact**: There is no automated testing for the frontend code, which may lead to undetected bugs and regressions
- **Recommendation**: Add test scripts and a test framework to the frontend project

## Security Review

### Confirmed Issues
1. **CORS Misconfiguration**: The backend uses `app.use(cors())` without any configuration, which defaults to allowing all origins. This is a confirmed security concern that could enable cross-origin attacks.

2. **Information Disclosure**: Both `/api/health` and `/api/version` endpoints expose version information without authentication, creating an information disclosure risk.

3. **DoS Vulnerability**: The `express.json()` middleware is used without size limits, creating a potential denial of service vector.

### Hardening Recommendations
1. Configure CORS with explicit allowed origins
2. Add authentication or network-level restrictions to health/version endpoints
3. Set body size limits on JSON parsing middleware
4. Create non-root users in both Dockerfiles

### Unverified Concerns
None identified - all findings are directly evidenced in the codebase.

## CI/CD Review

The CI/CD pipeline is well-structured with the following characteristics:

1. **Trigger Conditions**: Runs on pushes to main branch and version tags (v*.*.*)
2. **Node.js Setup**: Uses Node.js 22 with npm caching for both frontend and backend
3. **Build Process**: Installs dependencies and builds the frontend
4. **Docker Release**: Builds and pushes versioned Docker images to Docker Hub on tag pushes
5. **Secrets Management**: Uses GitHub secrets for Docker Hub credentials

**Observations**:
- The pipeline correctly handles multi-stage Docker builds for the frontend
- Version tagging is properly implemented for releases
- No test execution is present in the pipeline (consistent with missing test scripts)

## Docker / Infrastructure Review

### Backend Dockerfile
- Uses `node:22-alpine` base image
- Multi-stage build not implemented (single FROM statement)
- No non-root user configuration
- ARG/ENV for version injection is properly implemented

### Frontend Dockerfile
- Properly implements multi-stage build (builder stage → nginx stage)
- Uses `node:22-alpine` for build, `nginx:alpine` for runtime
- No non-root user configuration in nginx stage

### Docker Compose
- Defines both backend and frontend services
- Backend exposes port 3000 internally
- Frontend maps port 8080:80
- Frontend depends on backend service
- Environment variables properly configured

## Positive Findings

1. **Multi-stage Docker Build**: The frontend Dockerfile correctly implements a multi-stage build, separating the build environment from the runtime environment.

2. **Version Injection**: Both Dockerfiles properly support version injection via build arguments, enabling proper release versioning.

3. **CI/CD Structure**: The CI pipeline is well-organized with proper separation of concerns for dependency installation, building, and Docker image management.

4. **Environment Configuration**: Docker Compose properly configures environment variables and service dependencies.

5. **Proxy Configuration**: The nginx configuration correctly proxies API requests to the backend service.

## Recommended Action Plan

### Priority 1 (High - Security)
1. **Configure CORS**: Replace `app.use(cors())` with specific origin configuration:
   ```javascript
   app.use(cors({
     origin: ['https://yourdomain.com'],
     credentials: true
   }));
   ```

2. **Restrict Sensitive Endpoints**: Add authentication middleware or IP-based restrictions for `/api/health` and `/api/version` endpoints.

### Priority 2 (Medium - Security/Reliability)
3. **Add Body Size Limits**: Configure express.json() with size limits:
   ```javascript
   app.use(express.json({ limit: '10mb' }));
   ```

4. **Remove Version Endpoint**: Consider removing `/api/version` endpoint in production or adding authentication.

### Priority 3 (Low - Security Best Practices)
5. **Create Non-Root Users**: Update both Dockerfiles to create and use non-root users:
   ```dockerfile
   # Backend example
   RUN addgroup -g 1001 -S nodejs && \
       adduser -S nextjs -u 1001
   USER nextjs
   ```

### Priority 4 (Medium - Quality)
6. **Add Testing Framework**: Implement testing for both projects:
   - Backend: Add Jest or Mocha with supertest
   - Frontend: Add Vitest or Jest with React Testing Library

7. **Update CI Pipeline**: Add test execution steps to the CI workflow before building Docker images.