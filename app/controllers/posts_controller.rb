class PostsController < ApplicationController
  before_action :find_post, only: [:update]

  def index
    if category
      posts = category.posts.includes(:votes)
    else
      posts = Post.includes(:votes)
    end

    posts = posts.posts_by_state(posts_state).paginate(page: params[:page], per_page: 20)

    render cell: true, model: posts, options: { categories: Category.all, state: posts_state, votes: user_voted(posts),
      user: current_user }
  end

  def update
    @post.update(posts_params)

    posts_params[:state].present? ? redirect_to(:back) : render(nothing: true)
  end

  private

  def user_voted(posts)
    posts_ids = posts.ids
    if current_user
      current_user.votes.select { |vote| posts_ids.include?(vote.post_id) }
    else
      []
    end
  end

  def posts_params
    params.permit(:state, category_ids: [])
  end

  def posts_state
    @_state = Post.available_states.include?(params[:state]) ? params[:state] : Post.state.approved
  end

  def find_post
    @post = Post.find(params.fetch(:id))
  end

  def category
    @_category = Category.find_by(name: params[:category])
  end
end
