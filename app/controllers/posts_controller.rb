class PostsController < ApplicationController
  before_action :authenticate_user!, :check_permissions, only: [:update, :show]
  before_action :find_post, only: [:update, :show]

  def show
    comments = @post.comments

    render cell: :show, model: @post, options: { comments: comments.ordered_by_date, user_id: current_user.id }
  end

  def index
    if category
      posts = category.posts.includes(:votes)
    else
      posts = Post.includes(:votes)
    end

    posts = posts.includes(:categories).posts_by_state(posts_state).paginate(page: params[:page], per_page: 20)

    render cell: true, model: posts, options: { categories: Category.all, state: posts_state, votes: user_voted(posts),
      user: current_user }
  end

  def update
    @post.update(posts_params)

    if params[:redirrect_path].present?
      redirect_to(params[:redirrect_path])
    elsif posts_params[:state].present?
      redirect_to(:back)
    else
      render(nothing: true)
    end
  end

  private

  def back_url
    request.referer || root_path
  end

  def user_voted(posts)
    posts_ids = posts.ids
    if current_user
      current_user.votes.votes_posts(posts_ids)
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

  def check_permissions
    authorize User, :moderator?
  end
end
