export interface RouteConfig {
    name: string;
    path: string;
    component: string;
    title: string;
    description: string;
}

export class UIRouter {
    private currentRoute: RouteConfig | null = null;
    private routeMap: Map<string, RouteConfig> = new Map();
    private listeners: ((route: RouteConfig) => void)[] = [];

    constructor() {
        this.registerRoutes();
    }

    private registerRoutes() {
        const routes: RouteConfig[] = [
            {
                name: 'main',
                path: '/',
                component: 'index.html',
                title: 'Aetherium Genesis',
                description: 'Main Portal'
            },
            {
                name: 'nirodha',
                path: '/nirodha',
                component: 'gunui/nirodha_standby.html',
                title: 'Nirodha State',
                description: 'System Standby Mode'
            },
            {
                name: 'living-interface',
                path: '/living',
                component: 'gunui/living_interface.html',
                title: 'Living Interface',
                description: 'Vessel of Living Intent'
            },
            {
                name: 'generative',
                path: '/generative',
                component: 'gunui/generative_ui.html',
                title: 'Generative UI',
                description: 'AI-Driven UI Generation'
            },
            {
                name: 'particle',
                path: '/particle',
                component: 'gunui/particle_system.html',
                title: 'Particle System',
                description: 'Visual Particle Effects'
            },
            {
                name: 'light',
                path: '/light',
                component: 'gunui/light_testbed.html',
                title: 'Light Interaction',
                description: 'Light & AI Interaction Testbed'
            },
            {
                name: 'edge',
                path: '/edge',
                component: 'gunui/edge_gunui_connector.html',
                title: 'Edge Connector',
                description: 'Edge Computing Interface'
            }
        ];

        routes.forEach(route => this.routeMap.set(route.path, route));
    }

    public navigate(path: string): boolean {
        const route = this.routeMap.get(path);
        if (!route) {
            console.warn(`Route not found: ${path}`);
            return false;
        }

        this.currentRoute = route;
        this.notifyListeners(route);
        window.history.pushState({ path }, route.title, path);
        return true;
    }

    public getCurrentRoute(): RouteConfig | null {
        return this.currentRoute;
    }

    public getRoute(path: string): RouteConfig | undefined {
        return this.routeMap.get(path);
    }

    public getAllRoutes(): RouteConfig[] {
        return Array.from(this.routeMap.values());
    }

    public subscribe(listener: (route: RouteConfig) => void): () => void {
        this.listeners.push(listener);
        return () => {
            this.listeners = this.listeners.filter(l => l !== listener);
        };
    }

    private notifyListeners(route: RouteConfig) {
        this.listeners.forEach(listener => listener(route));
    }

    public handlePopState(event: PopStateEvent) {
        const path = window.location.pathname;
        const route = this.routeMap.get(path);
        if (route) {
            this.currentRoute = route;
            this.notifyListeners(route);
        }
    }
}

export const uiRouter = new UIRouter();