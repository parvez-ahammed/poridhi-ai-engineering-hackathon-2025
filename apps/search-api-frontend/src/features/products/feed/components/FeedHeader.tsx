import { useLocales } from "@/config/i18n";
import { useState } from "react";
import { useSearchParams } from "react-router-dom";

import { Button } from "@/components/ui/button";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";

import { tagsList } from "../../constants/tags.constant";

export const FeedHeader = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const [tags] = useState<string[]>(tagsList.map((tag) => tag.value));
    const [selectedTag, setSelectedTag] = useState<string>(
        searchParams.get("tags") || "all"
    );
    const {
        locale: { story: locale },
    } = useLocales();
    const sortOrder = searchParams.get("sort") || "desc";
    const orderBy = searchParams.get("order_by") || "createdAt";

    const handleSortOrderChange = (value: string) => {
        searchParams.set("order_by", orderBy || "createdAt");
        searchParams.set("sort", value);
        searchParams.set("page", "1");
        setSearchParams(searchParams);
    };

    const handleOrderByChange = (value: string) => {
        searchParams.set("sort", sortOrder || "desc");
        searchParams.set("order_by", value);
        setSearchParams(searchParams);
    };

    const handleTagChange = (tag: string) => {
        setSelectedTag(tag);
        searchParams.set("tags", tag);
        setSearchParams(searchParams);
    };
    const [open, setOpen] = useState(false);

    return (
        <div className="mb-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="hidden flex-wrap gap-2 sm:flex">
                {tags.map((tag) => (
                    <Button
                        key={tag}
                        variant="outline"
                        className={`border-black whitespace-nowrap ${
                            selectedTag === tag
                                ? "bg-black text-white"
                                : "text-black"
                        }`}
                        onClick={() => handleTagChange(tag)}
                    >
                        {tag}
                    </Button>
                ))}
            </div>

            <div className="hidden w-full flex-col gap-2 sm:flex sm:w-auto sm:flex-row sm:gap-4">
                <Select value={sortOrder} onValueChange={handleSortOrderChange}>
                    <SelectTrigger className="w-full sm:w-32">
                        <SelectValue placeholder="Sort order" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="asc">
                            {locale.cta.ascending}
                        </SelectItem>
                        <SelectItem value="desc">
                            {locale.cta.descending}
                        </SelectItem>
                    </SelectContent>
                </Select>

                <Select value={orderBy} onValueChange={handleOrderByChange}>
                    <SelectTrigger className="w-full sm:w-32">
                        <SelectValue placeholder="Sort by" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="createdAt">
                            {locale.cta.date}
                        </SelectItem>
                        <SelectItem value="title">
                            {locale.cta.title}
                        </SelectItem>
                        <SelectItem value="authorName">
                            {locale.cta.author}
                        </SelectItem>
                    </SelectContent>
                </Select>
            </div>

            <div className="sm:hidden">
                <Popover open={open} onOpenChange={setOpen}>
                    <PopoverTrigger asChild>
                        <Button variant="outline" className="w-full">
                            Filters
                        </Button>
                    </PopoverTrigger>
                    <PopoverContent className="flex w-full max-w-xs flex-col gap-3 p-4 sm:max-w-md">
                        <div className="flex w-full flex-wrap gap-2">
                            {tags.map((tag) => (
                                <Button
                                    key={tag}
                                    variant="outline"
                                    className={`border-black whitespace-nowrap ${
                                        selectedTag === tag
                                            ? "bg-black text-white"
                                            : "text-black"
                                    }`}
                                    onClick={() => handleTagChange(tag)}
                                >
                                    {tag}
                                </Button>
                            ))}
                        </div>

                        <Select
                            value={sortOrder}
                            onValueChange={handleSortOrderChange}
                        >
                            <SelectTrigger className="w-full">
                                <SelectValue placeholder="Sort order" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="desc">
                                    {locale.cta.descending}
                                </SelectItem>
                                <SelectItem value="asc">
                                    {locale.cta.ascending}
                                </SelectItem>
                            </SelectContent>
                        </Select>

                        <Select
                            value={orderBy}
                            onValueChange={handleOrderByChange}
                        >
                            <SelectTrigger className="w-full">
                                <SelectValue placeholder="Sort by" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="createdAt">
                                    {locale.cta.date}
                                </SelectItem>
                                <SelectItem value="title">
                                    {locale.cta.title}
                                </SelectItem>
                                <SelectItem value="authorName">
                                    {locale.cta.author}
                                </SelectItem>
                            </SelectContent>
                        </Select>
                    </PopoverContent>
                </Popover>
            </div>
        </div>
    );
};
