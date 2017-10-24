class PostsController < ApplicationController
  def index
    render cell: :index, model: posts
  end

  def show
    commit_post_view
    show_post_page
  end

  private

  def posts
    Posts::Filter.new(params)
      .filtered_posts
      .includes(:related_posts, :categories)
      .include_voted_by_user(current_user)
  end

  def commit_post_view
    PostView.create(user: current_user, post: post)
  end

  def post
    @_post ||= Post.include_voted_by_user(current_user).find(params[:id])
  end

  def show_post_page
    if post.show_internally?
      render cell: :show, model: post, layout: "post_layout"
    else
      redirect_to post.link
    end
  end
end
