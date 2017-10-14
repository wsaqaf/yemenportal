class PostsHeaderController < ApplicationController
  def show
    allow_to_return_header_to_unsafe_post_page
    render cell: :show, model: post, layout: "post_header_layout"
  end

  private

  def post
    Post.find(params[:id])
  end

  def allow_to_return_header_to_unsafe_post_page
    response.headers["X-Frame-Options"] = "ALLOWALL"
  end
end
