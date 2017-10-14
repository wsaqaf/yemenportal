class PostsController < ApplicationController
  def show
    if render_in_iframe?
      render cell: :show, model: post, layout: "iframe_layout"
    else
      redirect_to post.link
    end
  end

  private

  def render_in_iframe?
    FeatureToggle.iframe_proxy_enabled? || post.link.start_with?("https")
  end

  def post
    Post.find(params[:id])
  end
end
