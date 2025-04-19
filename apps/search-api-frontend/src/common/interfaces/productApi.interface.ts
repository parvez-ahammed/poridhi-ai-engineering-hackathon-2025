export interface ICreateStoryPayload {
    title: string;
    description: string;
    tags: string[];
}

interface ProductPayload {
    name: string;
    specification: string;
    price: number;
}

export interface IProduct {
    score: number;
    payload: ProductPayload;
}

export interface IGenerateStoryResponse {
    title: string;
    description: string;
}
