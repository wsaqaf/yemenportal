class PostsController < ApplicationController
  def index
    render cell: :index, model: posts
  end

  def show
    if post.show_internally?
      render cell: :show, model: post, layout: "post_layout"
    else
      redirect_to post.link
    end
  end

  private

  def post
    @_post ||= Post.include_voted_by_user(current_user).find(params[:id])
  end

  def posts
    Posts::Filter.new(params)
      .filtered_posts
      .includes(:related_posts, :categories)
      .include_voted_by_user(current_user)
  end
end
