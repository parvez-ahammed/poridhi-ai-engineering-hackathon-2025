import { Badge } from "@/components/ui/badge";
import {
    Tooltip,
    TooltipContent,
    TooltipTrigger,
} from "@/components/ui/tooltip";

export const TagsList = ({
    tags,
    truncateTags = true,
}: {
    tags: string[];
    truncateTags?: boolean;
}) => {
    const visibleTags = truncateTags ? tags.slice(0, 2) : tags;
    const hiddenTags = truncateTags ? tags.slice(2) : [];

    return (
        <div className="flex max-w-full flex-wrap items-center gap-2">
            {visibleTags.map((tag, index) => (
                <Badge
                    key={index}
                    variant="outline"
                    className="cursor-pointer text-xs font-normal"
                >
                    {tag}
                </Badge>
            ))}

            {hiddenTags.length > 0 && (
                <Tooltip>
                    <TooltipTrigger asChild>
                        <Badge
                            variant="outline"
                            className="text-primary cursor-pointer text-xs font-normal"
                        >
                            +{hiddenTags.length} More
                        </Badge>
                    </TooltipTrigger>
                    <TooltipContent className="max-w-[200px] rounded-md bg-white p-2 text-sm break-words text-gray-800 shadow-md">
                        <div className="max-h-[150px] overflow-y-auto">
                            {hiddenTags.map((tag, index) => (
                                <Badge
                                    variant="outline"
                                    className="text-primary m-1 cursor-pointer text-xs font-normal"
                                    key={index}
                                >
                                    {tag}
                                </Badge>
                            ))}
                        </div>
                    </TooltipContent>
                </Tooltip>
            )}
        </div>
    );
};
