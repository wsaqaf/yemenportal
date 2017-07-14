class PostsController < ApplicationController
  before_action :authenticate_user!, :check_permissions, only: [:update, :show]
  before_action :find_post, only: [:update, :show]

  def show
    comments = @post.comments

    render cell: :show, model: @post, options: { comments: comments.ordered_by_date, user_id: current_user.id }
  end

  def index
    render cell: true, model: posts, options: {
      state: posts_state,
      votes: user_voted(posts),
      user: current_user
    }
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

  def posts
    @_posts ||= begin
      posts = Post.includes(:votes)
      posts.includes(:categories).posts_by_state(posts_state).paginate(page: params[:page], per_page: 20)
    end
  end

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
    @_posts_params ||= begin
      posts_params = params.permit(:state, category_ids: [])

      if params[:tags].present?
        PostTag.where(user: current_user, post: @post).delete_all
        tags = params[:tags].reject(&:blank?)
        posts_params[:post_tags] = tags.map { |name| PostTag.new(user: current_user, post: @post, name: name) }
      end
      posts_params
    end
  end

  def posts_state
    @_state = Post.available_states.include?(params[:state]) ? params[:state] : Post.state.approved
  end

  def find_post
    @post = Post.find(params.fetch(:id))
  end

  def check_permissions
    authorize User, :moderator?
  end
end
