class PostsController < ApplicationController
  before_action :find_post, only: [:update]

  def index
    if Category.find_by(name: params[:category])
      posts = Category.find_by(name: params[:category]).posts
    else
      posts = Post.all
    end

    posts = posts.posts_by_state(posts_state).paginate(page: params[:page], per_page: 20)

    render cell: true, model: posts, options: { categories: Category.all, state: posts_state }
  end

  def update
    @post.update(state: params.fetch(:state))
    redirect_to :back
  end

  private

  def posts_state
    @_state = Post.state.values.include?(params[:state]) ? params[:state] : Post.state.approved
  end

  def find_post
    @post = Post.find(params.fetch(:id))
  end
end
