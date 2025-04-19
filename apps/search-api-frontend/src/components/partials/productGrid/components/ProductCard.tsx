import { useDeleteStory } from "@/common/hooks/useStoryApi.hook";
import { useLocales } from "@/config/i18n";
import { formatToMonthYear } from "@/lib/utils";
import { CalendarIcon, MoreVertical, User } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { Paragraph, Text } from "@/components/partials/typography";
import { Button } from "@/components/ui";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Avatar, AvatarImage } from "@/components/ui/avatar";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Separator } from "@/components/ui/separator";
import {
    Tooltip,
    TooltipContent,
    TooltipTrigger,
} from "@/components/ui/tooltip";

import { TagsList } from "./Taglist";

interface StoryCardProps {
    title: string;
    author: string;
    date: string;
    productId: string;
    description: string;
    likes?: number;
    tags?: string[];
    enableActions?: boolean;
    showDescription?: boolean;
    showTags?: boolean;
    summary?: string;
    truncateTags?: boolean;
}

export const StoryCard = ({
    productId,
    title,
    author,
    date,
    description,
    enableActions = false,
    tags = [],
    showDescription = true,
    showTags = true,
    summary,
    truncateTags = true,
}: StoryCardProps) => {
    const { deleteStory } = useDeleteStory();
    const navigate = useNavigate();
    const {
        locale: { story: locale },
    } = useLocales();

    const handleUpdate = () => {
        navigate("/products/create", {
            state: {
                productId: productId,
                initialTitle: title,
                initialDescription: description,
                initialTags: tags,
            },
        });
    };

    if (tags.includes("all")) {
        tags = tags.filter((tag) => tag !== "all");
    }

    const handleDelete = () => {
        deleteStory(productId);
    };

    const [isTruncatedTitle] = useState(title.length > 20);
    const [isTruncatedAuthor] = useState(author.length > 12);

    return (
        <div className="relative max-h-[300px] w-full rounded-lg border border-black bg-white p-4 text-left shadow-md transition hover:border-gray-400">
            {enableActions && (
                <div className="absolute top-2 right-2">
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8"
                            >
                                <MoreVertical className="h-4 w-4" />
                                <span className="sr-only">
                                    {locale.cta.openActionsMenu}
                                </span>
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="bg-white">
                            <DropdownMenuItem onClick={handleUpdate}>
                                {locale.cta.update}
                            </DropdownMenuItem>
                            <DropdownMenuItem
                                onSelect={(e) => e.preventDefault()}
                            >
                                <AlertDialog>
                                    <AlertDialogTrigger>
                                        <Text className="text-destructive-foreground w-full">
                                            {locale.cta.delete}
                                        </Text>
                                    </AlertDialogTrigger>
                                    <AlertDialogContent>
                                        <AlertDialogHeader>
                                            <AlertDialogTitle>
                                                {locale.alert.deleteTitle}
                                            </AlertDialogTitle>
                                            <AlertDialogDescription>
                                                {locale.alert.deleteDescription}
                                            </AlertDialogDescription>
                                        </AlertDialogHeader>
                                        <AlertDialogFooter>
                                            <AlertDialogCancel>
                                                {locale.cta.cancel}
                                            </AlertDialogCancel>
                                            <AlertDialogAction
                                                onClick={handleDelete}
                                            >
                                                {locale.cta.confirm}
                                            </AlertDialogAction>
                                        </AlertDialogFooter>
                                    </AlertDialogContent>
                                </AlertDialog>
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                </div>
            )}

            <Link
                to={`/products/${productId}`}
                className="hover:text-primary block"
            >
                <div className="flex w-full items-center gap-3">
                    <Avatar className="border-primary/20 h-10 w-10 border-2">
                        <AvatarImage src="/profile-photo-2.svg" alt={author} />
                    </Avatar>
                    <div className="w-full">
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <p className="line-clamp-1 w-full overflow-hidden text-2xl font-bold tracking-tight break-all">
                                    {title}
                                </p>
                            </TooltipTrigger>

                            {isTruncatedTitle && (
                                <TooltipContent className="max-w-[200px] rounded-md bg-white p-2 text-sm break-words text-gray-800 shadow-md">
                                    <p>{title}</p>
                                </TooltipContent>
                            )}
                        </Tooltip>

                        <div className="text-muted-foreground mt-1 flex flex-col gap-1 text-xs">
                            <div className="flex w-full items-center gap-3">
                                <div className="flex w-1/2 items-center gap-1">
                                    <User size={14} />
                                    <Tooltip>
                                        <TooltipTrigger asChild>
                                            <p className="line-clamp-1 w-full overflow-hidden tracking-tight break-all">
                                                {author}
                                            </p>
                                        </TooltipTrigger>
                                        {isTruncatedAuthor && (
                                            <TooltipContent className="max-w-[200px] rounded-md bg-white p-2 text-sm break-words text-gray-800 shadow-md">
                                                <p>{author}</p>
                                            </TooltipContent>
                                        )}
                                    </Tooltip>
                                </div>
                                <div className="flex items-center gap-1">
                                    <CalendarIcon size={12} />
                                    <span>{formatToMonthYear(date)}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <Separator className="my-3 border-1 border-gray-200" />
                {showTags && (
                    <TagsList tags={tags} truncateTags={truncateTags} />
                )}

                {showDescription && summary ? (
                    <Paragraph className="mt-2 line-clamp-3 text-sm">
                        {summary}
                    </Paragraph>
                ) : (
                    <Paragraph className="mt-2 text-sm">
                        No description available
                    </Paragraph>
                )}
            </Link>
        </div>
    );
};
