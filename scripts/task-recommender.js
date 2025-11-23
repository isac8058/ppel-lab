#!/usr/bin/env node

/**
 * PPEL Lab Website - Daily Task Recommender
 *
 * This script analyzes the codebase and generates task recommendations
 * based on code quality, performance, and feature completeness.
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, BorderStyle, AlignmentType } = require('docx');

class TaskRecommender {
    constructor() {
        this.tasks = [];
        this.researchTools = [];
        this.researchTrends = [];
        this.projectRoot = path.join(__dirname, '..');

        // Research keywords for arXiv search
        this.researchKeywords = {
            'ai-electronics': ['printed electronics machine learning', 'inkjet printing optimization neural network', 'flexible electronics AI'],
            'bio-printing': ['biosensor printing', 'bioelectronics inkjet', 'printed biosensor glucose'],
            'printed-memories': ['resistive switching printing', 'memristor inkjet', 'printed memory device'],
            'energy-storage': ['printed supercapacitor', 'flexible battery printing', 'energy harvesting printed'],
            'piezo-tribo': ['printed piezoelectric', 'triboelectric nanogenerator', 'piezoelectric polymer printing']
        };

        // Research tools database for PPEL Lab research areas
        this.toolsDatabase = {
            'ai-electronics': [
                { name: 'TensorFlow', category: 'AI/ML', description: '전자 회로 설계 자동화 및 결함 예측을 위한 딥러닝 프레임워크', url: 'https://tensorflow.org', tags: ['무료', 'Python'] },
                { name: 'PyTorch', category: 'AI/ML', description: '프린팅 파라미터 최적화를 위한 신경망 구축', url: 'https://pytorch.org', tags: ['무료', 'Python'] },
                { name: 'scikit-learn', category: 'AI/ML', description: '인쇄 품질 예측을 위한 머신러닝 라이브러리', url: 'https://scikit-learn.org', tags: ['무료', 'Python'] },
                { name: 'COMSOL Multiphysics', category: '시뮬레이션', description: '전자 소자의 다중 물리 시뮬레이션', url: 'https://comsol.com', tags: ['유료', '라이선스'] },
                { name: 'Jupyter Notebook', category: '개발환경', description: '데이터 분석 및 실험 결과 문서화', url: 'https://jupyter.org', tags: ['무료', 'Python'] },
                { name: 'AutoML (Google)', category: 'AI/ML', description: '코드 없이 머신러닝 모델 자동 생성', url: 'https://cloud.google.com/automl', tags: ['유료', '클라우드'] }
            ],
            'bio-printing': [
                { name: 'ImageJ/FIJI', category: '이미지 분석', description: '바이오센서 이미지 분석 및 세포 카운팅', url: 'https://imagej.net', tags: ['무료', 'Java'] },
                { name: 'CellProfiler', category: '이미지 분석', description: '자동화된 세포 이미지 분석', url: 'https://cellprofiler.org', tags: ['무료', 'Python'] },
                { name: 'BioRender', category: '시각화', description: '과학 일러스트레이션 및 논문 피겨 제작', url: 'https://biorender.com', tags: ['무료+유료', '웹'] },
                { name: 'GraphPad Prism', category: '통계', description: '생물학적 데이터 통계 분석 및 그래프 생성', url: 'https://graphpad.com', tags: ['유료', '라이선스'] },
                { name: 'SnapGene', category: '분자생물학', description: 'DNA/RNA 시퀀스 분석 및 설계', url: 'https://snapgene.com', tags: ['유료', '라이선스'] },
                { name: 'PyMOL', category: '분자 시각화', description: '3D 분자 구조 시각화', url: 'https://pymol.org', tags: ['무료+유료', 'Python'] }
            ],
            'printed-memories': [
                { name: 'OriginPro', category: '데이터 분석', description: 'I-V 특성 곡선 분석 및 그래프 생성', url: 'https://originlab.com', tags: ['유료', '라이선스'] },
                { name: 'MATLAB', category: '수치해석', description: '메모리 소자 특성 모델링 및 시뮬레이션', url: 'https://mathworks.com', tags: ['유료', '라이선스'] },
                { name: 'LTspice', category: '회로 시뮬레이션', description: 'SPICE 기반 전자회로 시뮬레이션', url: 'https://analog.com/ltspice', tags: ['무료', 'Windows'] },
                { name: 'Gwyddion', category: 'AFM 분석', description: 'SPM (AFM, STM) 데이터 분석', url: 'http://gwyddion.net', tags: ['무료', '오픈소스'] },
                { name: 'VESTA', category: '결정 구조', description: '3D 결정 구조 시각화', url: 'https://jp-minerals.org/vesta', tags: ['무료', '다중플랫폼'] },
                { name: 'CasaXPS', category: 'XPS 분석', description: 'X선 광전자 분광 데이터 분석', url: 'http://casaxps.com', tags: ['유료', 'Windows'] }
            ],
            'energy-storage': [
                { name: 'EC-Lab', category: '전기화학', description: '배터리/슈퍼캐패시터 전기화학 분석', url: 'https://biologic.net', tags: ['하드웨어 번들', '라이선스'] },
                { name: 'ZView', category: 'EIS 분석', description: '임피던스 스펙트럼 분석 및 피팅', url: 'https://scribner.com', tags: ['유료', 'Windows'] },
                { name: 'Nova', category: '전기화학', description: 'Autolab 전기화학 워크스테이션 소프트웨어', url: 'https://metrohm.com', tags: ['하드웨어 번들', '라이선스'] },
                { name: 'Battery Archive', category: '데이터베이스', description: '배터리 수명 데이터 공유 플랫폼', url: 'https://batteryarchive.org', tags: ['무료', '웹'] },
                { name: 'PyBaMM', category: '시뮬레이션', description: '배터리 모델링 파이썬 패키지', url: 'https://pybamm.org', tags: ['무료', 'Python'] },
                { name: 'Materials Project', category: '데이터베이스', description: '재료 특성 데이터베이스 및 검색', url: 'https://materialsproject.org', tags: ['무료', '웹'] }
            ],
            'piezo-tribo': [
                { name: 'ANSYS', category: '시뮬레이션', description: '압전 소자 유한요소 해석', url: 'https://ansys.com', tags: ['유료', '라이선스'] },
                { name: 'COMSOL Piezoelectric Module', category: '시뮬레이션', description: '압전 디바이스 멀티피직스 시뮬레이션', url: 'https://comsol.com', tags: ['유료', '라이선스'] },
                { name: 'LabVIEW', category: '데이터 수집', description: '압전 출력 측정 및 실시간 모니터링', url: 'https://ni.com/labview', tags: ['유료', '라이선스'] },
                { name: 'VESTA', category: '결정 구조', description: '압전 재료 결정 구조 분석', url: 'https://jp-minerals.org/vesta', tags: ['무료', '다중플랫폼'] },
                { name: 'Quantum ESPRESSO', category: 'DFT', description: '압전 상수 이론 계산 (제1원리)', url: 'https://quantum-espresso.org', tags: ['무료', 'Linux'] },
                { name: 'Mercury', category: '결정 구조', description: 'CIF 파일 시각화 및 분석', url: 'https://ccdc.cam.ac.uk', tags: ['무료', '다중플랫폼'] }
            ],
            'general': [
                { name: 'Zotero', category: '논문 관리', description: '논문 참고문헌 관리 및 인용', url: 'https://zotero.org', tags: ['무료', '다중플랫폼'] },
                { name: 'Overleaf', category: '논문 작성', description: '협업 LaTeX 논문 작성 플랫폼', url: 'https://overleaf.com', tags: ['무료+유료', '웹'] },
                { name: 'Grammarly', category: '논문 작성', description: '영어 논문 문법 및 스타일 검사', url: 'https://grammarly.com', tags: ['무료+유료', '웹'] },
                { name: 'Notion', category: '프로젝트 관리', description: '연구 노트 및 프로젝트 관리', url: 'https://notion.so', tags: ['무료+유료', '웹'] },
                { name: 'Slack', category: '협업', description: '연구팀 커뮤니케이션', url: 'https://slack.com', tags: ['무료+유료', '다중플랫폼'] },
                { name: 'GitHub', category: '코드 관리', description: '연구 코드 버전 관리 및 협업', url: 'https://github.com', tags: ['무료+유료', '웹'] }
            ]
        };
    }

    // Analyze the codebase
    async analyze() {
        console.log('🔍 Analyzing PPEL Lab codebase...\n');

        await this.checkImageOptimization();
        await this.checkAccessibility();
        await this.checkPerformance();
        await this.checkSEO();
        await this.checkCodeQuality();
        await this.checkFeatures();
        await this.checkSecurity();

        return this.tasks;
    }

    // Check for image optimization opportunities
    async checkImageOptimization() {
        const imageDir = path.join(this.projectRoot, 'image');

        if (fs.existsSync(imageDir)) {
            const images = this.getAllFiles(imageDir).filter(f =>
                /\.(jpg|jpeg|png|gif)$/i.test(f)
            );

            let largeImages = [];
            for (const img of images) {
                const stats = fs.statSync(img);
                const sizeKB = stats.size / 1024;
                if (sizeKB > 200) {
                    largeImages.push({ path: img, size: sizeKB });
                }
            }

            if (largeImages.length > 0) {
                this.tasks.push({
                    priority: 'high',
                    category: '이미지 최적화',
                    title: `${largeImages.length}개 이미지 압축 필요`,
                    description: `200KB 초과 이미지 발견. WebP 변환 및 압축 권장.`,
                    files: largeImages.slice(0, 3).map(i => path.basename(i.path)),
                    effort: 'low'
                });
            }

            // Check for WebP support
            const hasWebP = images.some(f => f.endsWith('.webp'));
            if (!hasWebP && images.length > 0) {
                this.tasks.push({
                    priority: 'medium',
                    category: '이미지 최적화',
                    title: 'WebP 이미지 포맷 도입',
                    description: '최신 WebP 포맷으로 변환하여 로딩 속도 개선',
                    effort: 'medium'
                });
            }
        }
    }

    // Check accessibility issues
    async checkAccessibility() {
        const htmlFile = path.join(this.projectRoot, 'index.html');

        if (fs.existsSync(htmlFile)) {
            const content = fs.readFileSync(htmlFile, 'utf8');

            // Check for alt tags
            const imgWithoutAlt = (content.match(/<img(?![^>]*alt=)[^>]*>/gi) || []).length;
            if (imgWithoutAlt > 0) {
                this.tasks.push({
                    priority: 'high',
                    category: '접근성',
                    title: `이미지 alt 속성 추가 (${imgWithoutAlt}개)`,
                    description: '스크린 리더 지원을 위해 모든 이미지에 alt 속성 필요',
                    effort: 'low'
                });
            }

            // Check for ARIA labels
            const hasAriaLabels = content.includes('aria-label');
            if (!hasAriaLabels) {
                this.tasks.push({
                    priority: 'medium',
                    category: '접근성',
                    title: 'ARIA 레이블 추가',
                    description: '인터랙티브 요소에 ARIA 레이블 추가하여 접근성 향상',
                    effort: 'medium'
                });
            }

            // Check for skip link
            const hasSkipLink = content.includes('skip-to-content') || content.includes('skip-link');
            if (!hasSkipLink) {
                this.tasks.push({
                    priority: 'low',
                    category: '접근성',
                    title: 'Skip Navigation 링크 추가',
                    description: '키보드 사용자를 위한 본문 바로가기 링크',
                    effort: 'low'
                });
            }
        }
    }

    // Check performance issues
    async checkPerformance() {
        const cssFile = path.join(this.projectRoot, 'styles.css');
        const jsFile = path.join(this.projectRoot, 'script.js');

        // Check CSS file size
        if (fs.existsSync(cssFile)) {
            const stats = fs.statSync(cssFile);
            const sizeKB = stats.size / 1024;
            if (sizeKB > 50) {
                this.tasks.push({
                    priority: 'medium',
                    category: '성능',
                    title: 'CSS 파일 최소화',
                    description: `CSS 파일 ${sizeKB.toFixed(1)}KB - 미니파이 및 미사용 스타일 제거 권장`,
                    effort: 'medium'
                });
            }
        }

        // Check JS file size
        if (fs.existsSync(jsFile)) {
            const stats = fs.statSync(jsFile);
            const sizeKB = stats.size / 1024;
            if (sizeKB > 30) {
                this.tasks.push({
                    priority: 'medium',
                    category: '성능',
                    title: 'JavaScript 파일 최소화',
                    description: `JS 파일 ${sizeKB.toFixed(1)}KB - 미니파이 권장`,
                    effort: 'low'
                });
            }
        }

        // Check for lazy loading
        const htmlFile = path.join(this.projectRoot, 'index.html');
        if (fs.existsSync(htmlFile)) {
            const content = fs.readFileSync(htmlFile, 'utf8');
            const hasLazyLoading = content.includes('loading="lazy"');
            if (!hasLazyLoading) {
                this.tasks.push({
                    priority: 'high',
                    category: '성능',
                    title: '이미지 Lazy Loading 적용',
                    description: '스크롤 시 이미지 로딩으로 초기 로딩 속도 개선',
                    effort: 'low'
                });
            }
        }
    }

    // Check SEO improvements
    async checkSEO() {
        const htmlFile = path.join(this.projectRoot, 'index.html');

        if (fs.existsSync(htmlFile)) {
            const content = fs.readFileSync(htmlFile, 'utf8');

            // Check for sitemap
            const sitemapFile = path.join(this.projectRoot, 'sitemap.xml');
            if (!fs.existsSync(sitemapFile)) {
                this.tasks.push({
                    priority: 'medium',
                    category: 'SEO',
                    title: 'Sitemap.xml 생성',
                    description: '검색 엔진 인덱싱을 위한 사이트맵 생성',
                    effort: 'low'
                });
            }

            // Check for robots.txt
            const robotsFile = path.join(this.projectRoot, 'robots.txt');
            if (!fs.existsSync(robotsFile)) {
                this.tasks.push({
                    priority: 'medium',
                    category: 'SEO',
                    title: 'robots.txt 생성',
                    description: '검색 엔진 크롤링 지침 파일 생성',
                    effort: 'low'
                });
            }

            // Check for structured data
            const hasStructuredData = content.includes('application/ld+json');
            if (!hasStructuredData) {
                this.tasks.push({
                    priority: 'medium',
                    category: 'SEO',
                    title: 'Schema.org 구조화 데이터 추가',
                    description: '검색 결과에서 풍부한 스니펫 표시를 위한 구조화 데이터',
                    effort: 'medium'
                });
            }
        }
    }

    // Check code quality
    async checkCodeQuality() {
        const htmlFile = path.join(this.projectRoot, 'index.html');

        if (fs.existsSync(htmlFile)) {
            const content = fs.readFileSync(htmlFile, 'utf8');

            // Check for inline styles
            const inlineStyles = (content.match(/style="[^"]+"/g) || []).length;
            if (inlineStyles > 20) {
                this.tasks.push({
                    priority: 'low',
                    category: '코드 품질',
                    title: `인라인 스타일 정리 (${inlineStyles}개)`,
                    description: '인라인 스타일을 CSS 클래스로 이동하여 유지보수성 향상',
                    effort: 'high'
                });
            }

            // Check for console.log
            const jsFile = path.join(this.projectRoot, 'script.js');
            if (fs.existsSync(jsFile)) {
                const jsContent = fs.readFileSync(jsFile, 'utf8');
                const consoleLogs = (jsContent.match(/console\.(log|warn|error)/g) || []).length;
                if (consoleLogs > 0) {
                    this.tasks.push({
                        priority: 'low',
                        category: '코드 품질',
                        title: `console.log 제거 (${consoleLogs}개)`,
                        description: '프로덕션 코드에서 디버그 로그 제거',
                        effort: 'low'
                    });
                }
            }
        }
    }

    // Check for missing features
    async checkFeatures() {
        const htmlFile = path.join(this.projectRoot, 'index.html');

        if (fs.existsSync(htmlFile)) {
            const content = fs.readFileSync(htmlFile, 'utf8');

            // Check for contact form
            const hasContactForm = content.includes('<form') && content.includes('submit');
            if (!hasContactForm) {
                this.tasks.push({
                    priority: 'medium',
                    category: '기능',
                    title: '연락처 폼 추가',
                    description: '이메일 팝업 대신 대학원생 문의 폼 구현',
                    effort: 'high'
                });
            }

            // Check for search functionality
            const hasSearch = content.includes('search') || content.includes('검색');
            if (!hasSearch) {
                this.tasks.push({
                    priority: 'low',
                    category: '기능',
                    title: '논문 검색 기능 추가',
                    description: '연도, 저자, 키워드별 논문 필터링 기능',
                    effort: 'high'
                });
            }

            // Check for 404 page
            const notFoundPage = path.join(this.projectRoot, '404.html');
            if (!fs.existsSync(notFoundPage)) {
                this.tasks.push({
                    priority: 'low',
                    category: '기능',
                    title: '404 에러 페이지 추가',
                    description: '사용자 친화적인 에러 페이지 생성',
                    effort: 'low'
                });
            }

            // Check for favicon
            const hasFavicon = content.includes('favicon') || content.includes('icon');
            if (!hasFavicon) {
                this.tasks.push({
                    priority: 'medium',
                    category: '기능',
                    title: 'Favicon 추가',
                    description: '브라우저 탭에 표시될 아이콘 추가',
                    effort: 'low'
                });
            }
        }
    }

    // Check security
    async checkSecurity() {
        const htmlFile = path.join(this.projectRoot, 'index.html');

        if (fs.existsSync(htmlFile)) {
            const content = fs.readFileSync(htmlFile, 'utf8');

            // Check for external links with target="_blank"
            const unsafeLinks = (content.match(/target="_blank"(?![^>]*rel=)/g) || []).length;
            if (unsafeLinks > 0) {
                this.tasks.push({
                    priority: 'medium',
                    category: '보안',
                    title: `외부 링크 보안 강화 (${unsafeLinks}개)`,
                    description: 'target="_blank" 링크에 rel="noopener noreferrer" 추가',
                    effort: 'low'
                });
            }
        }
    }

    // Recommend research tools based on day of week and research areas
    recommendResearchTools() {
        const today = new Date();
        const dayOfWeek = today.getDay(); // 0-6
        const dayOfMonth = today.getDate();

        // Rotate through research areas based on day
        const researchAreas = ['ai-electronics', 'bio-printing', 'printed-memories', 'energy-storage', 'piezo-tribo'];
        const todayArea = researchAreas[dayOfWeek % researchAreas.length];

        // Select tools for today's featured area
        const areaTools = this.toolsDatabase[todayArea] || [];
        const selectedAreaTools = this.shuffleArray([...areaTools]).slice(0, 2);

        // Also include general tools
        const generalTools = this.toolsDatabase['general'] || [];
        const selectedGeneralTools = this.shuffleArray([...generalTools]).slice(0, 1);

        // Combine and format
        this.researchTools = [
            {
                area: this.getAreaNameKo(todayArea),
                areaKey: todayArea,
                tools: selectedAreaTools
            },
            {
                area: '일반 연구 도구',
                areaKey: 'general',
                tools: selectedGeneralTools
            }
        ];

        return this.researchTools;
    }

    getAreaNameKo(areaKey) {
        const names = {
            'ai-electronics': 'AI 기반 프린티드 일렉트로닉스',
            'bio-printing': '바이오프린팅',
            'printed-memories': '프린티드 메모리',
            'energy-storage': '에너지 저장 소자',
            'piezo-tribo': '압전 및 마찰전기'
        };
        return names[areaKey] || areaKey;
    }

    shuffleArray(array) {
        // Use date as seed for consistent daily results
        const today = new Date().toISOString().split('T')[0];
        let seed = 0;
        for (let i = 0; i < today.length; i++) {
            seed += today.charCodeAt(i);
        }

        for (let i = array.length - 1; i > 0; i--) {
            const j = (seed * (i + 1)) % (i + 1);
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    // Fetch research trends from arXiv
    async fetchResearchTrends() {
        const today = new Date();
        const dayOfWeek = today.getDay();
        const researchAreas = ['ai-electronics', 'bio-printing', 'printed-memories', 'energy-storage', 'piezo-tribo'];
        const todayArea = researchAreas[dayOfWeek % researchAreas.length];

        const keywords = this.researchKeywords[todayArea] || [];
        const searchQuery = keywords[dayOfWeek % keywords.length] || 'printed electronics';

        console.log(`🔍 연구동향 검색: ${searchQuery}`);

        try {
            const papers = await this.fetchArxivPapers(searchQuery);
            this.researchTrends = {
                area: this.getAreaNameKo(todayArea),
                areaKey: todayArea,
                query: searchQuery,
                papers: papers.slice(0, 5) // Top 5 papers
            };
        } catch (error) {
            console.error('arXiv 검색 실패:', error.message);
            this.researchTrends = {
                area: this.getAreaNameKo(todayArea),
                areaKey: todayArea,
                query: searchQuery,
                papers: [],
                error: error.message
            };
        }

        return this.researchTrends;
    }

    // Fetch papers from arXiv API
    fetchArxivPapers(query) {
        return new Promise((resolve, reject) => {
            const encodedQuery = encodeURIComponent(query);
            const url = `https://export.arxiv.org/api/query?search_query=all:${encodedQuery}&start=0&max_results=10&sortBy=submittedDate&sortOrder=descending`;

            https.get(url, (res) => {
                let data = '';

                res.on('data', chunk => {
                    data += chunk;
                });

                res.on('end', () => {
                    try {
                        const papers = this.parseArxivResponse(data);
                        resolve(papers);
                    } catch (error) {
                        reject(error);
                    }
                });
            }).on('error', reject);
        });
    }

    // Parse arXiv XML response
    parseArxivResponse(xml) {
        const papers = [];
        const entryRegex = /<entry>([\s\S]*?)<\/entry>/g;
        let match;

        while ((match = entryRegex.exec(xml)) !== null) {
            const entry = match[1];

            const title = this.extractXmlValue(entry, 'title').replace(/\n/g, ' ').trim();
            const summary = this.extractXmlValue(entry, 'summary').replace(/\n/g, ' ').trim();
            const published = this.extractXmlValue(entry, 'published');
            const id = this.extractXmlValue(entry, 'id');

            // Extract authors
            const authorRegex = /<author>[\s\S]*?<name>(.*?)<\/name>[\s\S]*?<\/author>/g;
            const authors = [];
            let authorMatch;
            while ((authorMatch = authorRegex.exec(entry)) !== null) {
                authors.push(authorMatch[1]);
            }

            // Extract categories
            const categoryRegex = /<category[^>]*term="([^"]+)"/g;
            const categories = [];
            let catMatch;
            while ((catMatch = categoryRegex.exec(entry)) !== null) {
                categories.push(catMatch[1]);
            }

            papers.push({
                title,
                authors: authors.slice(0, 3), // First 3 authors
                summary: summary.substring(0, 300) + (summary.length > 300 ? '...' : ''),
                published: published.split('T')[0],
                url: id,
                categories: categories.slice(0, 3)
            });
        }

        return papers;
    }

    extractXmlValue(xml, tag) {
        const regex = new RegExp(`<${tag}[^>]*>([\\s\\S]*?)<\\/${tag}>`);
        const match = xml.match(regex);
        return match ? match[1] : '';
    }

    // Helper: Get all files recursively
    getAllFiles(dirPath, arrayOfFiles = []) {
        const files = fs.readdirSync(dirPath);

        files.forEach(file => {
            const filePath = path.join(dirPath, file);
            if (fs.statSync(filePath).isDirectory()) {
                arrayOfFiles = this.getAllFiles(filePath, arrayOfFiles);
            } else {
                arrayOfFiles.push(filePath);
            }
        });

        return arrayOfFiles;
    }

    // Generate report
    generateReport() {
        const today = new Date().toISOString().split('T')[0];
        const dayNames = ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일'];
        const dayName = dayNames[new Date().getDay()];

        let report = `# 📋 PPEL Lab 일일 보고서\n\n`;
        report += `**날짜:** ${today} (${dayName})\n`;
        report += `**웹사이트 개선 작업:** ${this.tasks.length}개\n`;
        report += `**연구 프로그램 추천:** ${this.researchTools.reduce((sum, area) => sum + area.tools.length, 0)}개\n\n`;

        report += `---\n\n`;

        // Research Trends Section
        if (this.researchTrends && this.researchTrends.papers && this.researchTrends.papers.length > 0) {
            report += `## 📚 최신 연구동향 (${this.researchTrends.area})\n\n`;
            report += `**검색 키워드:** ${this.researchTrends.query}\n\n`;

            this.researchTrends.papers.forEach((paper, index) => {
                report += `### ${index + 1}. ${paper.title}\n\n`;
                report += `- **저자:** ${paper.authors.join(', ')}${paper.authors.length >= 3 ? ' et al.' : ''}\n`;
                report += `- **발표일:** ${paper.published}\n`;
                report += `- **분야:** ${paper.categories.join(', ')}\n`;
                report += `- **링크:** [arXiv](${paper.url})\n\n`;
                report += `> ${paper.summary}\n\n`;
            });

            report += `---\n\n`;
        } else if (this.researchTrends && this.researchTrends.error) {
            report += `## 📚 최신 연구동향\n\n`;
            report += `⚠️ 연구동향 검색 중 오류 발생: ${this.researchTrends.error}\n\n`;
            report += `---\n\n`;
        }

        // Research Tools Section
        report += `## 🔬 오늘의 연구 프로그램 추천\n\n`;

        this.researchTools.forEach(areaData => {
            report += `### ${areaData.area}\n\n`;
            areaData.tools.forEach(tool => {
                report += `#### ${tool.name}\n`;
                report += `- **카테고리:** ${tool.category}\n`;
                report += `- **설명:** ${tool.description}\n`;
                report += `- **링크:** [${tool.url}](${tool.url})\n`;
                report += `- **태그:** ${tool.tags.join(', ')}\n\n`;
            });
        });

        report += `---\n\n`;

        // Tasks Section
        report += `## 🛠️ 웹사이트 개선 작업\n\n`;

        // Group by priority
        const highPriority = this.tasks.filter(t => t.priority === 'high');
        const mediumPriority = this.tasks.filter(t => t.priority === 'medium');
        const lowPriority = this.tasks.filter(t => t.priority === 'low');

        if (highPriority.length > 0) {
            report += `### 🔴 높은 우선순위 (${highPriority.length}개)\n\n`;
            highPriority.forEach(task => {
                report += this.formatTask(task);
            });
        }

        if (mediumPriority.length > 0) {
            report += `### 🟡 중간 우선순위 (${mediumPriority.length}개)\n\n`;
            mediumPriority.forEach(task => {
                report += this.formatTask(task);
            });
        }

        if (lowPriority.length > 0) {
            report += `### 🟢 낮은 우선순위 (${lowPriority.length}개)\n\n`;
            lowPriority.forEach(task => {
                report += this.formatTask(task);
            });
        }

        report += `---\n\n`;
        report += `## 📅 다음 연구 영역 예정\n\n`;

        const researchAreas = ['ai-electronics', 'bio-printing', 'printed-memories', 'energy-storage', 'piezo-tribo'];
        const todayIndex = new Date().getDay() % researchAreas.length;

        for (let i = 1; i <= 3; i++) {
            const nextIndex = (todayIndex + i) % researchAreas.length;
            const nextArea = researchAreas[nextIndex];
            report += `- **${i}일 후:** ${this.getAreaNameKo(nextArea)}\n`;
        }

        report += `\n---\n\n`;
        report += `*이 보고서는 자동으로 생성되었습니다. 매일 오전 9시(KST)에 업데이트됩니다.*\n`;

        return report;
    }

    formatTask(task) {
        let output = `### ${task.title}\n`;
        output += `- **카테고리:** ${task.category}\n`;
        output += `- **설명:** ${task.description}\n`;
        output += `- **예상 노력:** ${task.effort === 'low' ? '낮음 ⭐' : task.effort === 'medium' ? '중간 ⭐⭐' : '높음 ⭐⭐⭐'}\n`;
        if (task.files) {
            output += `- **관련 파일:** ${task.files.join(', ')}\n`;
        }
        output += '\n';
        return output;
    }

    // Generate Word document report
    async generateWordReport() {
        const today = new Date().toISOString().split('T')[0];
        const dayNames = ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일'];
        const dayName = dayNames[new Date().getDay()];

        const children = [];

        // Title
        children.push(new Paragraph({
            text: 'PPEL Lab 일일 보고서',
            heading: HeadingLevel.TITLE,
            alignment: AlignmentType.CENTER
        }));

        // Date info
        children.push(new Paragraph({
            children: [
                new TextRun({ text: '날짜: ', bold: true }),
                new TextRun(`${today} (${dayName})`)
            ]
        }));

        children.push(new Paragraph({
            children: [
                new TextRun({ text: '웹사이트 개선 작업: ', bold: true }),
                new TextRun(`${this.tasks.length}개`)
            ]
        }));

        children.push(new Paragraph({
            children: [
                new TextRun({ text: '연구 프로그램 추천: ', bold: true }),
                new TextRun(`${this.researchTools.reduce((sum, area) => sum + area.tools.length, 0)}개`)
            ]
        }));

        children.push(new Paragraph({ text: '' }));

        // Research Trends Section
        if (this.researchTrends && this.researchTrends.papers && this.researchTrends.papers.length > 0) {
            children.push(new Paragraph({
                text: `최신 연구동향 (${this.researchTrends.area})`,
                heading: HeadingLevel.HEADING_1
            }));

            children.push(new Paragraph({
                children: [
                    new TextRun({ text: '검색 키워드: ', bold: true }),
                    new TextRun(this.researchTrends.query)
                ]
            }));

            children.push(new Paragraph({ text: '' }));

            this.researchTrends.papers.forEach((paper, index) => {
                children.push(new Paragraph({
                    text: `${index + 1}. ${paper.title}`,
                    heading: HeadingLevel.HEADING_2
                }));

                children.push(new Paragraph({
                    children: [
                        new TextRun({ text: '저자: ', bold: true }),
                        new TextRun(`${paper.authors.join(', ')}${paper.authors.length >= 3 ? ' et al.' : ''}`)
                    ]
                }));

                children.push(new Paragraph({
                    children: [
                        new TextRun({ text: '발표일: ', bold: true }),
                        new TextRun(paper.published)
                    ]
                }));

                children.push(new Paragraph({
                    children: [
                        new TextRun({ text: '분야: ', bold: true }),
                        new TextRun(paper.categories.join(', '))
                    ]
                }));

                children.push(new Paragraph({
                    children: [
                        new TextRun({ text: '링크: ', bold: true }),
                        new TextRun(paper.url)
                    ]
                }));

                children.push(new Paragraph({
                    children: [
                        new TextRun({ text: paper.summary, italics: true })
                    ]
                }));

                children.push(new Paragraph({ text: '' }));
            });
        } else if (this.researchTrends && this.researchTrends.error) {
            children.push(new Paragraph({
                text: '최신 연구동향',
                heading: HeadingLevel.HEADING_1
            }));

            children.push(new Paragraph({
                children: [
                    new TextRun({ text: `연구동향 검색 중 오류 발생: ${this.researchTrends.error}`, color: 'FF0000' })
                ]
            }));
        }

        // Research Tools Section
        children.push(new Paragraph({
            text: '오늘의 연구 프로그램 추천',
            heading: HeadingLevel.HEADING_1
        }));

        this.researchTools.forEach(areaData => {
            children.push(new Paragraph({
                text: areaData.area,
                heading: HeadingLevel.HEADING_2
            }));

            areaData.tools.forEach(tool => {
                children.push(new Paragraph({
                    text: tool.name,
                    heading: HeadingLevel.HEADING_3
                }));

                children.push(new Paragraph({
                    children: [
                        new TextRun({ text: '카테고리: ', bold: true }),
                        new TextRun(tool.category)
                    ]
                }));

                children.push(new Paragraph({
                    children: [
                        new TextRun({ text: '설명: ', bold: true }),
                        new TextRun(tool.description)
                    ]
                }));

                children.push(new Paragraph({
                    children: [
                        new TextRun({ text: '링크: ', bold: true }),
                        new TextRun(tool.url)
                    ]
                }));

                children.push(new Paragraph({
                    children: [
                        new TextRun({ text: '태그: ', bold: true }),
                        new TextRun(tool.tags.join(', '))
                    ]
                }));

                children.push(new Paragraph({ text: '' }));
            });
        });

        // Tasks Section
        children.push(new Paragraph({
            text: '웹사이트 개선 작업',
            heading: HeadingLevel.HEADING_1
        }));

        const priorityGroups = [
            { name: '높은 우선순위', tasks: this.tasks.filter(t => t.priority === 'high'), color: 'FF0000' },
            { name: '중간 우선순위', tasks: this.tasks.filter(t => t.priority === 'medium'), color: 'FFA500' },
            { name: '낮은 우선순위', tasks: this.tasks.filter(t => t.priority === 'low'), color: '00FF00' }
        ];

        priorityGroups.forEach(group => {
            if (group.tasks.length > 0) {
                children.push(new Paragraph({
                    text: `${group.name} (${group.tasks.length}개)`,
                    heading: HeadingLevel.HEADING_2
                }));

                group.tasks.forEach(task => {
                    children.push(new Paragraph({
                        text: task.title,
                        heading: HeadingLevel.HEADING_3
                    }));

                    children.push(new Paragraph({
                        children: [
                            new TextRun({ text: '카테고리: ', bold: true }),
                            new TextRun(task.category)
                        ]
                    }));

                    children.push(new Paragraph({
                        children: [
                            new TextRun({ text: '설명: ', bold: true }),
                            new TextRun(task.description)
                        ]
                    }));

                    const effortText = task.effort === 'low' ? '낮음' : task.effort === 'medium' ? '중간' : '높음';
                    children.push(new Paragraph({
                        children: [
                            new TextRun({ text: '예상 노력: ', bold: true }),
                            new TextRun(effortText)
                        ]
                    }));

                    if (task.files) {
                        children.push(new Paragraph({
                            children: [
                                new TextRun({ text: '관련 파일: ', bold: true }),
                                new TextRun(task.files.join(', '))
                            ]
                        }));
                    }

                    children.push(new Paragraph({ text: '' }));
                });
            }
        });

        // Next research areas
        children.push(new Paragraph({
            text: '다음 연구 영역 예정',
            heading: HeadingLevel.HEADING_1
        }));

        const researchAreas = ['ai-electronics', 'bio-printing', 'printed-memories', 'energy-storage', 'piezo-tribo'];
        const todayIndex = new Date().getDay() % researchAreas.length;

        for (let i = 1; i <= 3; i++) {
            const nextIndex = (todayIndex + i) % researchAreas.length;
            const nextArea = researchAreas[nextIndex];
            children.push(new Paragraph({
                children: [
                    new TextRun({ text: `${i}일 후: `, bold: true }),
                    new TextRun(this.getAreaNameKo(nextArea))
                ]
            }));
        }

        children.push(new Paragraph({ text: '' }));
        children.push(new Paragraph({
            children: [
                new TextRun({ text: '이 보고서는 자동으로 생성되었습니다. 매일 오전 9시(KST)에 업데이트됩니다.', italics: true, size: 20 })
            ]
        }));

        // Create document
        const doc = new Document({
            sections: [{
                properties: {},
                children: children
            }]
        });

        return doc;
    }
}

// Main execution
async function main() {
    const recommender = new TaskRecommender();

    // Analyze codebase for tasks
    await recommender.analyze();

    // Recommend research tools
    recommender.recommendResearchTools();

    // Fetch research trends from arXiv
    await recommender.fetchResearchTrends();

    // Generate Word document
    const doc = await recommender.generateWordReport();
    const buffer = await Packer.toBuffer(doc);

    // Save Word document
    const today = new Date().toISOString().split('T')[0];
    const wordOutputPath = path.join(__dirname, '..', `PPEL_Lab_일일보고서_${today}.docx`);
    fs.writeFileSync(wordOutputPath, buffer);
    console.log(`\n✅ Word 보고서가 저장되었습니다: PPEL_Lab_일일보고서_${today}.docx`);

    // Also save as latest for email attachment
    const latestPath = path.join(__dirname, '..', 'DAILY_REPORT.docx');
    fs.writeFileSync(latestPath, buffer);

    // Return counts for GitHub Actions
    const toolCount = recommender.researchTools.reduce((sum, area) => sum + area.tools.length, 0);
    const paperCount = recommender.researchTrends.papers ? recommender.researchTrends.papers.length : 0;
    console.log(`📊 웹사이트 작업: ${recommender.tasks.length}개, 연구 프로그램: ${toolCount}개, 연구논문: ${paperCount}개`);

    return recommender.tasks.length;
}

main().catch(console.error);
