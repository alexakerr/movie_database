import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from app.models import Genre as GenreModel, Movie as MovieModel, db


class GenreType(SQLAlchemyObjectType): #graphQL types for genre and movie - defines them
    class Meta:
        model = GenreModel

    movies = graphene.List(lambda: MovieType)# defines a field to resolve movies w a genre

    def resolve_movies(root, info):
        return root.movies.all()

class MovieType(SQLAlchemyObjectType):
    class Meta:
        model = MovieModel
        exclude_fields = ("genres",)

    genres = graphene.List(GenreType) # defines a field to resolve movies w a movie

    def resolve_genres(root, info):
        return root.genres


class Query(graphene.ObjectType): # defines the query object with resolver functions
    genres = graphene.List(GenreType)
    movies = graphene.List(MovieType)
    movie = graphene.Field(MovieType, movie_id=graphene.ID(required=True))
    genre = graphene.Field(GenreType, genre_id=graphene.ID(required=True))
    movies_by_genre = graphene.List(MovieType, genre_id=graphene.Int(required=True))
    genre_by_movie = graphene.Field(GenreType, movie_id=graphene.Int(required=True))

    
    def resolve_genres(root, info):  #fetch all genres
        return GenreModel.query.all()

    def resolve_movies(root, info): # fetch movies
        return MovieModel.query.all()
    
    def resolve_movie(root, info, movie_id):   # fetch a specific movie by its id
        return MovieModel.query.get(movie_id)
    
    def resolve_genre(root, info, genre_id):  # fetch a specific genre by its id
        return GenreModel.query.get(genre_id)

    
    def resolve_movies_by_genre(root, info, genre_id): # get the movies that belong to specific genre
        genre = GenreModel.query.get(genre_id)
        if genre:
            return genre.movies
        return []

    
    def resolve_genre_by_movie(root, info, movie_id): #get the genre of a specific movie
        movie = MovieModel.query.get(movie_id)
        if movie:
            return movie.genres[0] if movie.genres else None
        return None


class CreateGenre(graphene.Mutation): # defines mutations for creating/updating/deleting genres
    class Arguments:
        name = graphene.String(required=True)

    genre = graphene.Field(GenreType)

    def mutate(root, info, name):
        if not name or len(name) > 50:
            raise ValueError("Genre name must not be empty and should be less than 50 characters.")

        
        genre = GenreModel(name=name) # creates new genre instance
        db.session.add(genre) # adds to the db session and commits
        db.session.commit()
        return CreateGenre(genre=genre)

class UpdateGenre(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String(required=True)

    genre = graphene.Field(GenreType)

    def mutate(root, info, id, name):
        genre = db.session.get(GenreModel, id)
        if not genre:
            raise ValueError("Genre not found!")
        if not name or len(name) > 30:
            raise ValueError("Invalid Entry, Try again!")

        genre.name = name
        db.session.commit()
        return UpdateGenre(genre=genre)

class DeleteGenre(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.String()

    def mutate(root, info, id):
        genre = db.session.get(GenreModel, id)
        if not genre:
            raise ValueError(f"Genre with id {id} does not exist.")

      
        db.session.delete(genre)  # deletes the genre
        db.session.commit()  
        return DeleteGenre(success=True)

class Mutation(graphene.ObjectType):
    create_genre = CreateGenre.Field()
    update_genre = UpdateGenre.Field()
    delete_genre = DeleteGenre.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)