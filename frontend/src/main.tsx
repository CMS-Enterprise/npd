import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { BrowserRouter, Route, Routes } from "react-router"

import "@cmsgov/design-system/dist/fonts/opensans-bold-webfont.woff2"
import "@cmsgov/design-system/dist/fonts/opensans-regular-webfont.woff2"
import "./index.css"

// USWDS javascript behaviors
import "@uswds/uswds"

import "./i18n.ts"

import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { AuthenticatedRoute } from "./components/AuthenticatedRoute"
import { ErrorBoundary, ErrorFallback } from "./components/ErrorBoundary.tsx"
import { FeatureFlagRoute } from "./components/FeatureFlagRoute"
import { Developers } from "./pages/Developers"
import { Landing } from "./pages/Landing"
import { Layout } from "./pages/Layout"
import { Login } from "./pages/Login"
import { NotFound } from "./pages/NotFound.tsx"
import {
  Organization,
  OrganizationSearch,
} from "./pages/Organization"
import { 
  Practitioner,
  PractitionerSearch
} from "./pages/Practitioner"
import { Search } from "./pages/Search"
import { FrontendSettingsProvider } from "./state/FrontendSettingsProvider"

const queryClient = new QueryClient()

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <FrontendSettingsProvider>
          <ErrorBoundary fallback={ErrorFallback}>
            <Routes>
              <Route element={<Layout />}>
                <Route path="/accounts/login/" element={<Login />} />

                <Route element={<AuthenticatedRoute />}>
                  <Route index element={<Landing />} />
                  <Route path="/developers" element={<Developers />} />

                  <Route element={<FeatureFlagRoute name="SEARCH_APP" />}>
                    <Route path="/search" element={<Search />} />
                    <Route path="/organizations">
                      <Route path="search" element={<OrganizationSearch />} />
                      <Route
                        path=":organizationId"
                        element={<Organization />}
                      />
                    </Route>
                    <Route path="/practitioners">
                      <Route path="search" element={<PractitionerSearch />} />
                      <Route
                        path=":practitionerId"
                        element={<Practitioner />}
                      />
                    </Route>
                  </Route>
                </Route>

                <Route path="*" element={<NotFound />} />
              </Route>
            </Routes>
          </ErrorBoundary>
        </FrontendSettingsProvider>
      </QueryClientProvider>
    </BrowserRouter>
  </StrictMode>,
)
