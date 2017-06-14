class CommentsController < ApplicationController
  before_action :authenticate_user!
  before_action :find_post, only: [:create, :index]
  respond_to :js, only: [:crate, :destroy]

  def index
    render cell: true, model: @post
  end

  def create
    comment = Comment.new(comment_params)

    if comment.save
      render json: { html: concept("posts/comments/cell", comment, user_id: current_user.id).call }, status: :ok
    else
      render json: { errors: comment.errors.messages }, status: :bad_request
    end
  end

  def destroy
    comment = Comment.find(params[:id])
    head status: :ok if comment.user == current_user && comment.destroy
  end

  private

  def back_url
    request.referer || root_path
  end

  def comment_params
    @_comment_patams = params.require(:comment).permit(:body).merge(post: @post, user: current_user)
  end

  def find_post
    @post = Post.find(params.fetch(:post_id))
  end
end
