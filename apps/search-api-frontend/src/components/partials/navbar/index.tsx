import { Menu, Search, X } from "lucide-react";
import { useState } from "react";
import { Link, useLocation } from "react-router-dom";

import { SearchBar } from "./components/SearchBar";
import { Text } from "@/components/partials/typography";
import { Button } from "@/components/ui";

export const Navbar = () => {
    const location = useLocation();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [mobileSearchOpen, setMobileSearchOpen] = useState(false);

    const isBaseRoute = location.pathname === "/";

    const toggleMobileMenu = () => {
        setMobileMenuOpen(!mobileMenuOpen);
        if (mobileSearchOpen) setMobileSearchOpen(false);
    };

    const toggleMobileSearch = () => {
        setMobileSearchOpen(!mobileSearchOpen);
        if (mobileMenuOpen) setMobileMenuOpen(false);
    };

    return (
        <header className="sticky top-0 z-20 border-y-1 border-black bg-white/80 px-2 backdrop-blur-md supports-[backdrop-filter]:bg-white/70">
            <div className="container mx-auto max-w-7xl">
                <div className="flex h-16 items-center justify-between">
                    <div className="flex items-center">
                        <Link to="/" className="flex items-center">
                            <Text className="bg-black px-3 py-1 text-xl font-bold text-white">
                                Searchy
                            </Text>
                        </Link>
                    </div>

                    {isBaseRoute && (
                        <>
                            <SearchBar />
                            {!mobileSearchOpen && (
                                <Button
                                    className="p-2 md:hidden"
                                    onClick={toggleMobileSearch}
                                    aria-label="Search"
                                >
                                    <Search className="h-5 w-5 text-black" />
                                </Button>
                            )}
                        </>
                    )}

                    {!mobileSearchOpen && (
                        <Button
                            className="p-2 md:hidden"
                            onClick={toggleMobileMenu}
                            aria-label={
                                mobileMenuOpen ? "Close menu" : "Open menu"
                            }
                        >
                            {mobileMenuOpen ? (
                                <X className="h-5 w-5 text-black" />
                            ) : (
                                <Menu className="h-5 w-5 text-black" />
                            )}
                        </Button>
                    )}
                </div>

                {isBaseRoute && mobileSearchOpen && (
                    <div className="bg-white/60 pb-4 backdrop-blur-md md:hidden">
                        <SearchBar
                            isMobile
                            onClose={toggleMobileSearch}
                            autoFocus
                        />
                    </div>
                )}
            </div>
        </header>
    );
};
