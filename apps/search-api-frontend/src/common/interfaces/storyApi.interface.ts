export interface ICreateStoryPayload {
    title: string;
    description: string;
    tags: string[];
}

export interface IStory {
    id: string;
    title: string;
    description: string;
    authorName: string;
    authorUsername: string;
    date?: string;
    tags: string[];
    likes: number;
    authorId: string;
    summary?: string;
    createdAt?: string;
}

export interface IGenerateStoryResponse {
    title: string;
    description: string;
}
