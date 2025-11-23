        // Get current date
        const today = new Date();
        const formatDate = (date) => {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}.${month}.${day}`;
        };

        // Generate recent dates for news
        const generateRecentDates = () => {
            const dates = [];
            for (let i = 0; i < 10; i++) {
                const date = new Date(today);
                date.setDate(date.getDate() - i);
                dates.push(formatDate(date));
            }
            return dates;
        };

        const recentDates = generateRecentDates();

        // Research area news data - updated daily with relevant news
        const researchNews = {
            'ai-electronics': {
                ko: [
                    {
                        date: recentDates[0],
                        title: 'AI 기반 전자 회로 설계 자동화 기술 개발',
                        content: 'PPEL 연구팀이 인공지능을 활용한 프린티드 전자 회로 자동 설계 시스템을 개발했습니다. 이 시스템은 설계 시간을 90% 단축시킵니다.',
                        source: 'PPEL Lab News'
                    },
                    {
                        date: recentDates[1],
                        title: '머신러닝으로 인쇄 전자 소자 불량률 예측',
                        content: '새로운 머신러닝 알고리즘을 통해 인쇄 공정 중 발생하는 불량을 사전에 예측하고 방지하는 기술이 개발되었습니다.',
                        source: 'Tech Innovation Daily'
                    },
                    {
                        date: recentDates[2],
                        title: 'AI 최적화 잉크젯 프린팅 기술 상용화 임박',
                        content: '인공지능이 실시간으로 프린팅 파라미터를 조정하여 인쇄 품질을 향상시키는 기술이 곧 산업 현장에 적용될 예정입니다.',
                        source: 'Electronics Weekly'
                    }
                ],
                en: [
                    {
                        date: recentDates[0],
                        title: 'AI-Powered Automated Electronic Circuit Design Developed',
                        content: 'PPEL research team has developed an AI-based automated design system for printed electronic circuits, reducing design time by 90%.',
                        source: 'PPEL Lab News'
                    },
                    {
                        date: recentDates[1],
                        title: 'Machine Learning Predicts Defects in Printed Electronics',
                        content: 'A new machine learning algorithm can predict and prevent defects during the printing process of electronic devices.',
                        source: 'Tech Innovation Daily'
                    },
                    {
                        date: recentDates[2],
                        title: 'AI-Optimized Inkjet Printing Technology Near Commercialization',
                        content: 'Technology that uses AI to adjust printing parameters in real-time for improved print quality is set to be implemented in industry.',
                        source: 'Electronics Weekly'
                    }
                ]
            },
            'bio-printing': {
                ko: [
                    {
                        date: recentDates[0],
                        title: '바이오센서 기반 실시간 건강 모니터링 시스템 개발',
                        content: 'PPEL 연구팀이 개발한 새로운 바이오센서는 땀을 통해 실시간으로 건강 상태를 모니터링할 수 있습니다.',
                        source: 'BioMed Today'
                    },
                    {
                        date: recentDates[1],
                        title: '3D 프린팅 마이크로니들 패치 임상시험 승인',
                        content: '무통 약물 전달을 위한 3D 프린팅 마이크로니들 패치가 식약처 임상시험 승인을 받았습니다.',
                        source: 'Medical News Korea'
                    },
                    {
                        date: recentDates[3],
                        title: '그래핀 기반 DNA 검출 센서 민감도 100배 향상',
                        content: '새로운 그래핀 나노구조를 활용한 DNA 검출 센서가 기존 대비 100배 향상된 민감도를 보였습니다.',
                        source: 'Nano Letters'
                    }
                ],
                en: [
                    {
                        date: recentDates[0],
                        title: 'Real-time Health Monitoring System Using Biosensors Developed',
                        content: 'New biosensor developed by PPEL team can monitor health status in real-time through sweat analysis.',
                        source: 'BioMed Today'
                    },
                    {
                        date: recentDates[1],
                        title: '3D Printed Microneedle Patch Approved for Clinical Trials',
                        content: '3D printed microneedle patches for painless drug delivery have received clinical trial approval from regulatory authorities.',
                        source: 'Medical News Korea'
                    },
                    {
                        date: recentDates[3],
                        title: 'Graphene-based DNA Detection Sensor Shows 100x Improvement',
                        content: 'New graphene nanostructure-based DNA detection sensor demonstrates 100-fold improvement in sensitivity.',
                        source: 'Nano Letters'
                    }
                ]
            },
            'printed-memories': {
                ko: [
                    {
                        date: recentDates[0],
                        title: '차세대 프린티드 메모리 소자 데이터 보존 10년 달성',
                        content: '새로 개발된 프린티드 메모리 소자가 10년 이상의 데이터 보존 능력을 입증했습니다.',
                        source: 'Memory Tech Review'
                    },
                    {
                        date: recentDates[2],
                        title: '플렉시블 메모리 소자 굽힘 테스트 10만회 통과',
                        content: 'PPEL 연구팀의 플렉시블 메모리가 10만회 굽힘 테스트에서도 안정적인 성능을 유지했습니다.',
                        source: 'Flexible Electronics Journal'
                    },
                    {
                        date: recentDates[4],
                        title: '탄소 기반 저항 변화 메모리 상용화 가속',
                        content: '친환경 탄소 소재를 활용한 차세대 메모리 소자의 대량 생산 기술이 확립되었습니다.',
                        source: 'Green Tech News'
                    }
                ],
                en: [
                    {
                        date: recentDates[0],
                        title: 'Next-Gen Printed Memory Achieves 10-Year Data Retention',
                        content: 'Newly developed printed memory devices demonstrate data retention capability of over 10 years.',
                        source: 'Memory Tech Review'
                    },
                    {
                        date: recentDates[2],
                        title: 'Flexible Memory Device Passes 100,000 Bending Cycles',
                        content: 'PPEL team\'s flexible memory maintains stable performance after 100,000 bending test cycles.',
                        source: 'Flexible Electronics Journal'
                    },
                    {
                        date: recentDates[4],
                        title: 'Carbon-based Resistive Memory Commercialization Accelerates',
                        content: 'Mass production technology established for eco-friendly carbon-based next-generation memory devices.',
                        source: 'Green Tech News'
                    }
                ]
            },
            'energy-storage': {
                ko: [
                    {
                        date: recentDates[0],
                        title: 'MXene 기반 슈퍼캐패시터 에너지 밀도 신기록',
                        content: 'PPEL 연구팀이 개발한 MXene 복합체 슈퍼캐패시터가 세계 최고 수준의 에너지 밀도를 달성했습니다.',
                        source: 'Energy Storage News'
                    },
                    {
                        date: recentDates[1],
                        title: '3D 프린팅 배터리 5분 충전 기술 개발',
                        content: '새로운 3D 프린팅 기술로 제작된 배터리가 5분 내 80% 충전이 가능한 성능을 보였습니다.',
                        source: 'Battery Technology Today'
                    },
                    {
                        date: recentDates[3],
                        title: '인쇄형 에너지 저장 소자 시장 2025년 100억 달러 전망',
                        content: '프린티드 에너지 저장 소자 시장이 급성장하여 2025년 100억 달러 규모에 달할 것으로 예상됩니다.',
                        source: 'Market Research Report'
                    }
                ],
                en: [
                    {
                        date: recentDates[0],
                        title: 'MXene-based Supercapacitor Sets New Energy Density Record',
                        content: 'MXene composite supercapacitor developed by PPEL team achieves world-leading energy density levels.',
                        source: 'Energy Storage News'
                    },
                    {
                        date: recentDates[1],
                        title: '3D Printed Battery Achieves 5-Minute Charging',
                        content: 'New 3D printed battery technology demonstrates 80% charge capability within 5 minutes.',
                        source: 'Battery Technology Today'
                    },
                    {
                        date: recentDates[3],
                        title: 'Printed Energy Storage Market to Reach $10B by 2025',
                        content: 'The printed energy storage device market is rapidly growing and expected to reach $10 billion by 2025.',
                        source: 'Market Research Report'
                    }
                ]
            },
            'piezo-tribo': {
                ko: [
                    {
                        date: recentDates[0],
                        title: 'PVDF 기반 나노발전기 효율 40% 향상',
                        content: '새로운 페로브스카이트 나노필러를 적용한 PVDF 나노발전기가 기존 대비 40% 향상된 효율을 보였습니다.',
                        source: 'Nano Energy News'
                    },
                    {
                        date: recentDates[2],
                        title: '웨어러블 에너지 하베스팅 상용 제품 출시',
                        content: 'PPEL 기술이 적용된 첫 상용 웨어러블 에너지 하베스팅 제품이 시장에 출시되었습니다.',
                        source: 'Wearable Tech Magazine'
                    },
                    {
                        date: recentDates[4],
                        title: '종이 기반 마찰전기 발전기로 IoT 센서 구동 성공',
                        content: '친환경 종이 기반 마찰전기 발전기가 IoT 센서를 독립적으로 구동하는데 성공했습니다.',
                        source: 'Green Energy Journal'
                    }
                ],
                en: [
                    {
                        date: recentDates[0],
                        title: 'PVDF-based Nanogenerator Efficiency Improved by 40%',
                        content: 'PVDF nanogenerator with new perovskite nanofillers shows 40% efficiency improvement over existing devices.',
                        source: 'Nano Energy News'
                    },
                    {
                        date: recentDates[2],
                        title: 'First Commercial Wearable Energy Harvesting Product Launched',
                        content: 'The first commercial wearable energy harvesting product using PPEL technology has been released to market.',
                        source: 'Wearable Tech Magazine'
                    },
                    {
                        date: recentDates[4],
                        title: 'Paper-based Triboelectric Generator Powers IoT Sensors',
                        content: 'Eco-friendly paper-based triboelectric generator successfully powers IoT sensors independently.',
                        source: 'Green Energy Journal'
                    }
                ]
            }
        };

 // News data
const newsData = {
    ko: [
        {
            date: '2025.06.21',
            title: 'Chemical Engineering Journal 논문 게재',
content: '그래픽 탄소 질화물의 압전 성능 연구가 Chemical Engineering Journal (IF: 13.4)에 게재되었습니다.',            
            tag: '논문'
        },
        {
            date: '2025.01.10',
            title: '우수 중견연구자 지원사업 선정',
            content: '2024년 5월 한국연구재단 우수 중견연구자 지원사업에 선정되었습니다.',
            tag: '연구과제'
        },
        {
            date: '2024.05.20',
            title: 'PMMA 기반 마이크로니들 특허 전북대 홍보자료 선정',
            content: 'PMMA 기반 마이크로니들 특허의 우수성을 인정받아 전북대학교 홍보자료로 선정되었습니다.',
            tag: '홍보',
            hasVideo: true,
            videoPath: 'Video/PMMA.mp4'
        }
    ],
    en: [
        {
            date: '2025.06.21',
            title: 'Publication in Chemical Engineering Journal',
            content: 'Graphitic carbon nitride for piezoelectric performance has been published in Chemical Engineering Journal (IF: 13.4).',
            tag: 'Publication'
        },
        {
            date: '2025.01.10',
            title: 'Selected for Mid-Career Researcher Program',
            content: 'Selected for the NRF Mid-Career Researcher Program in May 2024.',
            tag: 'Grant'
        },
        {
            date: '2024.05.20',
            title: 'PMMA Microneedle Patent Selected for JBNU Promotion',
            content: 'Our PMMA-based microneedle patent was selected as JBNU promotional material for its excellence.',
            tag: 'Promotion',
            hasVideo: true,
            videoPath: 'Video/PMMA.mp4'
        }
    ]
};

        // Language Toggle
        let currentLang = 'en';
        const langToggle = document.getElementById('langToggle');
        
        langToggle.addEventListener('click', () => {
            currentLang = currentLang === 'ko' ? 'en' : 'ko';
            langToggle.textContent = currentLang === 'ko' ? 'EN' : 'KO';
            updateLanguage();
            updateNews();
            updateViewAllButton();
        });

        function updateLanguage() {
            document.querySelectorAll('[data-ko][data-en]').forEach(element => {
                element.textContent = element.getAttribute(`data-${currentLang}`);
            });
        }

        // Update News
        function updateNews() {
            const newsGrid = document.getElementById('newsGrid');
            const news = newsData[currentLang];
            
            newsGrid.innerHTML = news.map(item => `
                <div class="news-item standard-card ${item.hasVideo ? 'has-video' : ''}" ${item.hasVideo ? `onclick="showVideoModal('${item.videoPath}')"` : ''}>
                    <div class="news-date">${item.date}</div>
                    <h3 class="news-title">${item.title}</h3>
                    <p class="news-content">${item.content}</p>
<div class="news-bottom">                        <span class="news-tag">${item.tag}</span>
                        ${item.hasVideo ? '<span style="color: var(--accent-blue); font-size: 1.2rem;">▶️</span>' : ''}
                    </div>
                </div>
            `).join('');
        }

        // Video Modal Functions
        function showVideoModal(videoPath) {
            const modal = document.createElement('div');
            modal.className = 'video-modal';
            modal.innerHTML = `
                <div class="video-modal-content">
                    <span class="video-close" onclick="closeVideoModal()">&times;</span>
                    <video controls autoplay style="width: 100%; max-height: 80vh;">
                        <source src="${videoPath}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </div>
            `;
            document.body.appendChild(modal);
            modal.style.display = 'block';
        }
// Professor Tab Functions
function showTab(tabName) {
    // 모든 탭 버튼과 콘텐츠 숨기기
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => button.classList.remove('active'));
    tabContents.forEach(content => content.classList.remove('active'));
    
    // 선택된 탭 활성화
    const activeButton = Array.from(tabButtons).find(button => 
        button.textContent.toLowerCase() === tabName.toLowerCase()
    );
    if (activeButton) {
        activeButton.classList.add('active');
    }
    
    const activeContent = document.getElementById(tabName + '-tab');
    if (activeContent) {
        activeContent.classList.add('active');
    }
}
        function closeVideoModal() {
            const modal = document.querySelector('.video-modal');
            if (modal) {
                modal.remove();
            }
        }

        // Initialize news
        updateNews();

        // Theme Toggle
        const themeToggle = document.getElementById('themeToggle');
        const body = document.body;
        
        themeToggle.addEventListener('click', () => {
            body.classList.toggle('light-mode');
            const isLightMode = body.classList.contains('light-mode');
            themeToggle.textContent = isLightMode ? '☀️' : '🌙';
        });

        // Mobile menu toggle
        const mobileMenuToggle = document.getElementById('mobileMenuToggle');
        const navLinks = document.getElementById('navLinks');

        mobileMenuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });

        // Close mobile menu when clicking on a link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
            });
        });

        // Research Papers Modal Functions
        function showResearchPapers(area) {
            const modal = document.getElementById('papersModal');
            const papersList = document.getElementById('papersList');
            const papersTitle = document.getElementById('papersTitle');
            
            // Get area name
            const areaNames = {
                'ai-electronics': currentLang === 'ko' ? 'AI 기반 프린티드 일렉트로닉스' : 'AI-Printed Electronics',
                'bio-printing': currentLang === 'ko' ? '바이오프린팅' : 'Bio-printing',
                'printed-memories': currentLang === 'ko' ? '프린티드 메모리' : 'Printed Memories',
                'energy-storage': currentLang === 'ko' ? '프린티드 슈퍼캐패시터 및 배터리' : 'Printed Supercapacitors & Batteries',
                'piezo-tribo': currentLang === 'ko' ? '압전 및 마찰전기' : 'Piezo and Triboelectricity'
            };
            
            papersTitle.textContent = areaNames[area] + ' - ' + (currentLang === 'ko' ? '최신 뉴스' : 'Latest News');
            
            // Clear previous content
            papersList.innerHTML = '';
            
            // Add news items
            const news = researchNews[area][currentLang] || [];
            
            // Add update notice
            const updateNotice = document.createElement('div');
            updateNotice.style.cssText = 'text-align: center; padding: 20px; background: rgba(0, 212, 255, 0.1); border-radius: 10px; margin-bottom: 20px;';
            updateNotice.innerHTML = `
                <p style="color: var(--accent-blue); font-weight: 600; margin: 0;">
                    ${currentLang === 'ko' ? '🔄 매일 업데이트되는 최신 뉴스' : '🔄 Daily Updated Latest News'}
                </p>
                <p style="font-size: 0.9rem; color: var(--text-secondary); margin: 5px 0 0 0;">
                    ${currentLang === 'ko' ? `마지막 업데이트: ${formatDate(today)}` : `Last updated: ${formatDate(today)}`}
                </p>
            `;
            papersList.appendChild(updateNotice);
            
            // Add news items
            news.forEach(item => {
                const newsDiv = document.createElement('div');
                newsDiv.className = 'paper-item';
                newsDiv.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span style="color: var(--accent-blue); font-size: 0.9rem;">${item.date}</span>
                        <span style="background: var(--gradient-1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 0.85rem; font-weight: 600;">${item.source}</span>
                    </div>
                    <h3 class="paper-title">${item.title}</h3>
                    <p style="color: var(--text-secondary); line-height: 1.6; margin-top: 10px;">${item.content}</p>
                `;
                papersList.appendChild(newsDiv);
            });
            
            // Add more news coming soon notice
            const moreNews = document.createElement('div');
            moreNews.style.cssText = 'text-align: center; padding: 30px; margin-top: 30px; border-top: 1px solid var(--border-color);';
            moreNews.innerHTML = `
                <p style="color: var(--text-secondary); font-style: italic;">
                    ${currentLang === 'ko' ? '더 많은 뉴스가 곧 업데이트됩니다...' : 'More news coming soon...'}
                </p>
            `;
            papersList.appendChild(moreNews);
            
            // Show modal
            modal.style.display = 'block';
        }

        function closePapersModal() {
            document.getElementById('papersModal').style.display = 'none';
        }

        // Close modal when clicking outside
        window.addEventListener('click', (event) => {
            const modal = document.getElementById('papersModal');
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });

        // Typing Effect with Multiple Languages
        function initTypingEffect() {
            const typingText = document.getElementById('typingText');
            const typingCursor = document.getElementById('typingCursor');
            if (!typingText || !typingCursor) return;
            
            const phrases = [
                { text: '미래를 인쇄하다', lang: 'ko' },
                { text: 'Printing the Future', lang: 'en' },
                { text: '打印未来', lang: 'zh' },
                { text: '未来を印刷する', lang: 'ja' },
                { text: 'भविष्य को प्रिंट करना', lang: 'hi' },  // Hindi
                { text: 'مستقبل کو پرنٹ کرنا', lang: 'ur' },  // Urdu
                { text: 'Mencetak Masa Depan', lang: 'ms' },  // Malay
                { text: 'Imprimer l\'Avenir', lang: 'fr' },
                { text: 'Drucken die Zukunft', lang: 'de' },
                { text: 'Imprimiendo el Futuro', lang: 'es' },
                { text: 'Stampare il Futuro', lang: 'it' }
            ];
            
            let phraseIndex = 0;
            let charIndex = 0;
            let isDeleting = false;
            let isWaiting = false;
            
            // Show cursor immediately
            typingCursor.style.display = 'inline-block';
            
            function typeWriter() {
                const currentPhrase = phrases[phraseIndex];
                
                if (isWaiting) {
                    setTimeout(() => {
                        isWaiting = false;
                        isDeleting = true;
                        typeWriter();
                    }, 2000); // Wait 2 seconds before deleting
                    return;
                }
                
                if (!isDeleting) {
                    // Typing
                    if (charIndex < currentPhrase.text.length) {
                        typingText.textContent = currentPhrase.text.substring(0, charIndex + 1);
                        charIndex++;
                        setTimeout(typeWriter, 100);
                    } else {
                        // Finished typing
                        isWaiting = true;
                        typeWriter();
                    }
                } else {
                    // Deleting
                    if (charIndex > 0) {
                        typingText.textContent = currentPhrase.text.substring(0, charIndex - 1);
                        charIndex--;
                        setTimeout(typeWriter, 50); // Delete faster
                    } else {
                        // Finished deleting, move to next phrase
                        isDeleting = false;
                        phraseIndex = (phraseIndex + 1) % phrases.length;
                        setTimeout(typeWriter, 500); // Small pause before next phrase
                    }
                }
            }
            
            // Start typing after a short delay
            setTimeout(typeWriter, 800);
        }

        // Update View All Publications button text on language change
        function updateViewAllButton() {
            const viewAllBtn = document.querySelector('.view-all-btn .btn-text');
            if (viewAllBtn) {
                const parentBtn = viewAllBtn.closest('.view-all-btn');
                viewAllBtn.textContent = parentBtn.getAttribute(`data-${currentLang}`);
            }
        }

        // Initialize typing effect on page load
        window.addEventListener('load', () => {
            setTimeout(() => {
                document.getElementById('loader').classList.add('hidden');
                initTypingEffect();
            }, 500);
        });

        // Number Counter Animation
        function animateCounter(element, target) {
            let current = 0;
            const increment = target / 100;
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                    if (target >= 1000) {
                        element.textContent = (target / 1000).toFixed(1) + 'k';
                    } else {
                        element.textContent = Math.floor(current);
                    }
                } else {
                    element.textContent = Math.floor(current);
                }
            }, 20);
        }

        /* Animate visitor counts */
        function animateVisitorCounts() {
            const visitorCounts = document.querySelectorAll('.visitor-count');
            visitorCounts.forEach(count => {
                const target = parseInt(count.getAttribute('data-count'));
                animateCounter(count, target);
            });
        }

        // Intersection Observer for animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // Animate elements
                    if (entry.target.classList.contains('standard-card')) {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }
                    
                    // Animate stat numbers
                    if (entry.target.classList.contains('stat-number')) {
                        const target = parseInt(entry.target.getAttribute('data-count'));
                        animateCounter(entry.target, target);
                        observer.unobserve(entry.target);
                    }
                    
                    // Animate visitor card
                    if (entry.target.classList.contains('visitor-card')) {
                        animateVisitorCounts();
                        observer.unobserve(entry.target);
                    }
                }
            });
        }, observerOptions);

        // Observe elements - 애니메이션 효과 제거
        document.querySelectorAll('.stat-number').forEach(stat => {
            observer.observe(stat);
        });

        // Observe visitor card
        document.querySelectorAll('.visitor-card').forEach(card => {
            observer.observe(card);
        });

        // Navbar scroll effect
        window.addEventListener('scroll', () => {
            const navbar = document.getElementById('navbar');
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });

        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Create particle effect
        function createParticles() {
            const particlesContainer = document.getElementById('particles');
            const particleCount = 50;
            
            for (let i = 0; i < particleCount; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.animationDelay = Math.random() * 10 + 's';
                particle.style.animationDuration = (10 + Math.random() * 10) + 's';
                particlesContainer.appendChild(particle);
            }
        }

        // Initialize particles
        createParticles();
// Initialize particles
createParticles();

// Simple Email Popup Functions
function showEmailPopup(event) {
    event.preventDefault();
    const popup = document.getElementById('emailPopup');
    const backdrop = document.getElementById('emailBackdrop');
    
    backdrop.classList.add('show');
    setTimeout(() => {
        popup.classList.add('show');
    }, 100);
}

function closeEmailPopup() {
    const popup = document.getElementById('emailPopup');
    const backdrop = document.getElementById('emailBackdrop');
    const tooltip = document.getElementById('copyTooltip');
    
    popup.classList.remove('show');
    tooltip.classList.remove('show');
    
    setTimeout(() => {
        backdrop.classList.remove('show');
    }, 300);
}

function copyEmail() {
    const email = 'smlim@jbnu.ac.kr';
    
    // Copy to clipboard
    navigator.clipboard.writeText(email).then(() => {
        const tooltip = document.getElementById('copyTooltip');
        tooltip.innerHTML = currentLang === 'ko' ? '복사되었습니다!' : 'Copied!';
        tooltip.classList.add('show');
        
        // Hide tooltip and close popup after delay
        setTimeout(() => {
            closeEmailPopup();
        }, 1000);
    });
}

// Show tooltip on hover
document.addEventListener('DOMContentLoaded', () => {
    const emailAddress = document.querySelector('.email-address');
    const tooltip = document.getElementById('copyTooltip');
    
    if (emailAddress && tooltip) {
        emailAddress.addEventListener('mouseenter', () => {
            if (!tooltip.classList.contains('show')) {
                tooltip.innerHTML = currentLang === 'ko' ? '클릭하여 복사' : 'Click to copy';
                tooltip.classList.add('show');
            }
        });
        
        emailAddress.addEventListener('mouseleave', () => {
            if (tooltip.innerHTML.includes('copy') || tooltip.innerHTML.includes('복사')) {
                tooltip.classList.remove('show');
            }
        });
    }
});

// Close with ESC key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && document.getElementById('emailPopup').classList.contains('show')) {
        closeEmailPopup();
    }
});
// PPEL 로고 전기 효과
function initElectricEffect() {
    const letters = document.querySelectorAll('.hero-title .letter');
    if (!letters.length) return;
    
    // 전기 번개 생성 함수
    function createElectricBolt(element, x, y) {
        const bolt = document.createElement('div');
        bolt.className = 'electric-bolt';
        
        const angle = Math.random() * 360;
        const length = 20 + Math.random() * 30;
        
        bolt.style.height = length + 'px';
        bolt.style.left = x + 'px';
        bolt.style.top = y + 'px';
        bolt.style.transform = `translate(-50%, -50%) rotate(${angle}deg)`;
        
        element.appendChild(bolt);
        setTimeout(() => bolt.remove(), 300);
    }
    
    // 전기 파티클 생성 함수
    function createElectricParticle(element, x, y) {
        const particle = document.createElement('div');
        particle.className = 'electric-particle';
        
        const angle = Math.random() * Math.PI * 2;
        const velocity = 30 + Math.random() * 60;
        const tx = Math.cos(angle) * velocity;
        const ty = Math.sin(angle) * velocity;
        
        particle.style.left = x + 'px';
        particle.style.top = y + 'px';
        particle.style.setProperty('--tx', tx + 'px');
        particle.style.setProperty('--ty', ty + 'px');
        
        element.appendChild(particle);
        setTimeout(() => particle.remove(), 600);
    }
    
    // 각 글자에 이벤트 추가
    letters.forEach(letter => {
        let isHovering = false;
        
        letter.addEventListener('mouseenter', function(e) {
            isHovering = true;
            
            const rect = letter.getBoundingClientRect();
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            // 전기 효과 생성
            for (let i = 0; i < 3; i++) {
                setTimeout(() => {
                    if (isHovering) {
                        createElectricBolt(letter, centerX, centerY);
                        for (let j = 0; j < 3; j++) {
                            createElectricParticle(letter, centerX, centerY);
                        }
                    }
                }, i * 50);
            }
        });
        
        letter.addEventListener('mouseleave', function() {
            isHovering = false;
        });
        
        // 클릭시 효과
        letter.addEventListener('click', function(e) {
            e.preventDefault();
            
            const rect = letter.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            for (let i = 0; i < 5; i++) {
                createElectricBolt(letter, x, y);
            }
            
            for (let i = 0; i < 10; i++) {
                createElectricParticle(letter, x, y);
            }
        });
    });
}

// 페이지 로드 후 전기 효과 초기화
window.addEventListener('load', () => {
    setTimeout(() => {
        initElectricEffect();
    }, 1000);
});
// Initialize particles
createParticles();
