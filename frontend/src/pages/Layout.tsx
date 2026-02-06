import { Outlet } from "react-router"
import { Footer } from "../components/Footer"
import { Header } from "../components/Header"
import { LoadingIndicator } from "../components/LoadingIndicator"
import { useFrontendSettings } from "../hooks/useFrontendSettings"
import layout from "./Layout.module.css"

// A react-router compatible page wrapper.
export const Layout = () => {
  const { loading } = useFrontendSettings()

  // do not render a page until frontend settings have finished loading
  return (
    <div className={layout.pageWrapper}>
      <Header />
      <main className={layout.main}>
        {loading ? <LoadingIndicator /> : <Outlet />}
      </main>
      <Footer />
    </div>
  )
}
