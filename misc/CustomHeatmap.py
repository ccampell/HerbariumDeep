import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches
import matplotlib.transforms
from matplotlib import cm

num_unique_initializers = 3
num_unique_optimizers = 2


def plot_parent_grid(hyperparams_df, colormap, figure, grid_width, grid_length):
    num_children = grid_width * grid_length
    num_grandchildren = 4
    gs0 = gridspec.GridSpec(grid_width, grid_length)
    for i in range(num_children):
        optimizer_strs = ['NESTEROV', 'ADAM']
        optimizer = optimizer_strs[i // grid_length]
        initializer_strs = ['HE_NORMAL', 'HE_UNIFORM', 'NORMAL_TRUNCATED', 'HE_NORMAL', 'HE_UNIFORM', 'NORMAL_TRUNCATED']
        initializer = initializer_strs[i]
        activation_strs_x = ['LEAKY_RELU', 'LEAKY_RELU', 'ELU', 'ELU', 'LEAKY_RELU', 'LEAKY_RELU', 'ELU', 'ELU']
        activation_strs_y = ['ELU', 'ELU', 'ELU', 'ELU', 'LEAKY_RELU', 'LEAKY_RELU', 'LEAKY_RELU', 'LEAKY_RELU']
        gs00 = gs0[i].subgridspec(2, 4, wspace=0.0, hspace=0.0)
        # grandchildren_indices = [k for k in range(num_grandchildren*2)]
        # chunked = [grandchildren_indices[i:i + 2] for i in range(0, len(grandchildren_indices), 2)]
        # relu_indices = np.array([chunked[i] for i in range(len(chunked)) if i % 2 == 0]).flatten()
        # elu_indices = np.array([chunked[i] for i in range(len(chunked)) if i % 2 != 0]).flatten()
        for j in range(num_grandchildren*2):
            activation_x = activation_strs_x[j]
            activation_y = activation_strs_y[j]
            if activation_x == activation_y:
                activation = activation_x
            else:
                activation = None
            train_batch_strs = ['TB=10', 'TB=20']
            train_batch = train_batch_strs[j % 2]
            hyperparams_optim_subset = hyperparams_df[hyperparams_df['optimizer'] == 'OPTIM_%s' % optimizer]
            hyperparams_init_subset = hyperparams_optim_subset[hyperparams_optim_subset['initializer'] == 'INIT_%s' % initializer]
            if train_batch == 'TB=10':
                hyperparams_subset = hyperparams_init_subset[hyperparams_init_subset['train_batch_size'] == 10]
            elif train_batch == 'TB=20':
                hyperparams_subset = hyperparams_init_subset[hyperparams_init_subset['train_batch_size'] == 20]
            if activation is not None:
                hyperparams_subset = hyperparams_subset[hyperparams_subset['activation'] == 'ACTIVATION_%s' % activation]
                assert hyperparams_subset.shape[0] == 1
            ax = plt.Subplot(figure, gs00[j])
            ax.set_xticks([0, 1, 2])
            ax.set_yticks([0, 1, 2])
            ax.set_yticklabels('')
            if activation is not None:
                ax.patch.set_facecolor(colormap(hyperparams_subset.iloc[0].best_epoch_loss))
                print(hyperparams_subset.head())
            if i < num_children // 2:
                # Nesterov row
                if j < num_grandchildren:
                    # First row of top row.
                    ax.set_xticklabels(['', train_batch, ''])
                    ax.xaxis.tick_top()
                    if i == 0:
                        # This is the first child of 6 [0, 1, ..., 5]
                        if j == 0:
                            # This is the first grandchild of 8 [0, 1, ..., 7]
                            ax.set_yticklabels([optimizer, activation_y, ''])
                            # ax.patch.set_facecolor(colormap(0.5))
                            # if activation is not None:
                            #     ax.patch.set_facecolor(colormap(hyperparams_subset.iloc[0].best_epoch_loss))
                            #     print(hyperparams_subset.head())
                            # ax.patch.set_facecolor()
                else:
                    # Second row of top row:
                    ax.set_xticklabels('')
                    if i == 0:
                        if j == num_grandchildren:
                            # This is the fifth child of 8
                            ax.set_yticklabels(['', activation_y, ''])
            else:
                # Adam row.
                if j < num_grandchildren:
                    # First row of bottom row.
                    ax.set_xticklabels('')
                    if i == num_children // 2:
                        # First grandchild of 8
                        if j == 0:
                            ax.set_yticklabels([optimizer, activation_y, ''])
                else:
                    # Second row of bottom row:
                    if j == num_grandchildren:
                        # This is the fifth grandchild of 8
                        ax.set_xticklabels(['', '', activation_x])
                        if i == num_children // 2:
                            # Bottom left
                            ax.set_yticklabels(['', activation_y, ''])
                    elif j == num_grandchildren + 1:
                        ax.set_xticklabels(['', '', initializer])
                        # Create offset transform by 5 points in x direction
                        dx = 0/72.
                        dy = -10/72.
                        offset = matplotlib.transforms.ScaledTranslation(dx, dy, figure.dpi_scale_trans)
                        for label in ax.xaxis.get_majorticklabels():
                            label.set_transform(label.get_transform() + offset)
                    elif j == num_grandchildren + 2:
                        ax.set_xticklabels(['', '', activation_x])
                    else:
                        ax.set_xticklabels('')
            figure.add_subplot(ax)
    return figure

def plot_children_grid(figure, grid_width, grid_length):
    parent_grid = figure._gridspecs[0]
    for i in range(parent_grid._nrows * parent_grid._ncols):
        gs0i = gridspec.GridSpecFromSubplotSpec(grid_width, grid_length, subplot_spec=parent_grid[i])
        for j in range(grid_width):
            for k in range(grid_length):
                # ax00j = plt.subplot(gs0i[j, k])
                figure.add_subplot(gs0i[j, k])
    figure.add_gridspec(grid_width, grid_length)
    return figure

# def plot_grandchildren_grid(children_grid_width, children_grid_length, parent_grid_width, parent_grid_length, new_grid_width, new_grid_height, parent_grid):
#     num_grids = (parent_grid_width*parent_grid_length)*(children_grid_width*children_grid_length)
#     for i in range(num_grids):
#         gs00i = gridspec.GridSpecFromSubplotSpec(new_grid_width, new_grid_height, subplot_spec=parent_grid[i])
#         for j in range(new_grid_width):
#             for k in range(new_grid_height):
#                 ax000j = plt.subplot(gs00i[j, k])

def plot_grandchildren_grid(figure, grid_width, grid_length):
    parent_grid = figure._gridspecs[0]
    children_grid = figure._gridspecs[1]
    num_grids = parent_grid._nrows * parent_grid._ncols * children_grid._nrows * children_grid._ncols
    for i in range(parent_grid._nrows * parent_grid._ncols):
        for j in range(children_grid._nrows * children_grid._ncols):
            gs00i = gridspec.GridSpecFromSubplotSpec(grid_width, grid_length, subplot_spec=children_grid[j])
            for k in range(grid_width):
                for l in range(grid_length):
                    figure.add_subplot(gs00i[k, l])

    figure.add_gridspec(grid_width, grid_length)
    return figure


def main():
    __path = 'C:\\Users\\ccamp\\Documents\\GitHub\\HerbariumDeep\\tests\\gs_train_hyperparams.pkl'
    df = pd.read_pickle(__path)
    plt.show()
    fig = plt.figure(figsize=(8, 8), constrained_layout=False)
    cmap = cm.get_cmap('viridis', 12)
    fig = plot_parent_grid(hyperparams_df=df, colormap=cmap, figure=fig, grid_width=2, grid_length=3)
    plt.subplots_adjust(wspace=0, hspace=0)
    # cax = fig.add_axes(list(np.arange(0, 12, 1)))

    # base = plt.cm.get_cmap('viridis')
    # color_list = base(np.linspace(0, 1, 10))
    # cmap_name = base.name + str(10)
    # cmap = cm.colors.ListedColormap(colors=color_list, name=cmap_name, N=10)
    # cax = fig.add_axes([0.27, 0.8, 0.5, 0.05])
    # fig.colorbar(mappable=cmap, cax=cax)
    # source: https://medium.com/data-science-canvas/way-to-show-colorbar-without-calling-imshow-or-scatter-4a378058316
    scalar_mappable = cm.ScalarMappable(cmap=plt.cm.get_cmap('viridis'), norm=plt.Normalize(vmin=0, vmax=1))
    scalar_mappable._A = []
    plt.colorbar(scalar_mappable)

    # plt.colorbar(mappable=cmap, cax=cax)
    # plt.subplots_adjust(wspace=0, hspace=0)
    # fig = plot_children_grid(figure=fig, grid_width=2, grid_length=2)
    # fig = plot_grandchildren_grid(figure=fig, grid_width=2, grid_length=2)
    # grid = plot_grandchildren_grid(children_grid_width=2, children_grid_length=2, parent_grid_width=2, parent_grid_length=3, new_grid_width=2, new_grid_height=2, parent_grid=grid)
    # grid = plot_children_grid(grid_width=2, grid_length=2, parent_grid=grid)
    plt.show()

if __name__ == '__main__':
    main()

# Plot parent grid:
# plt.show()
# gs0 = gridspec.GridSpec(2, 3)
# ax1 = plt.subplot(gs0[0, 0])
# ax2 = plt.subplot(gs0[0, 1])
# ax3 = plt.subplot(gs0[0, 2])
# ax4 = plt.subplot(gs0[1, 0])
# ax5 = plt.subplot(gs0[1, 1])
# ax6 = plt.subplot(gs0[1, 2])
# # collapse parent grid:
# plt.subplots_adjust(wspace=0, hspace=0)
#
# # Plot child grids:
# gs00 = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec=gs0[0])
# ax001 = plt.subplot(gs00[0, 0])
# ax002 = plt.subplot(gs00[0, 1])
# ax003 = plt.subplot(gs00[1, 0])
# ax004 = plt.subplot(gs00[1, 1])
# gs01 = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec=gs0[1])
# ax011 = plt.subplot(gs01[0, 0])
# ax012 = plt.subplot(gs01[0, 1])
# ax013 = plt.subplot(gs01[1, 0])
# ax014 = plt.subplot(gs01[1, 1])
# gs02 = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec=gs0[2])
# ax021 = plt.subplot(gs02[0, 0])
# ax022 = plt.subplot(gs02[0, 1])
# ax023 = plt.subplot(gs02[1, 0])
# ax024 = plt.subplot(gs02[1, 1])
# gs03 = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec=gs0[3])
# ax031 = plt.subplot(gs03[0, 0])
# ax032 = plt.subplot(gs03[0, 1])
# ax033 = plt.subplot(gs03[1, 0])
# ax034 = plt.subplot(gs03[1, 1])
# gs04 = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec=gs0[4])
# ax041 = plt.subplot(gs04[0, 0])
# ax042 = plt.subplot(gs04[0, 1])
# ax043 = plt.subplot(gs04[1, 0])
# ax044 = plt.subplot(gs04[1, 1])
# gs05 = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec=gs0[5])
# ax051 = plt.subplot(gs05[0, 0])
# ax052 = plt.subplot(gs05[0, 1])
# ax053 = plt.subplot(gs05[1, 0])
# ax054 = plt.subplot(gs05[1, 1])
#
# # plot grandchildren grids:
# gs000 = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec=gs00[0])
# ax0001 = plt.subplot(gs000[0, 0])
# ax0002 = plt.subplot(gs000[0, 1])
# ax0003 = plt.subplot(gs000[1, 0])
# ax0004 = plt.subplot(gs000[1, 1])
# gs001 = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec=gs00[1])
# gs002 = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec=gs00[2])
#
# # Create inner layer:
# gs00 = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec=gs0[0])
# ax01 = plt.subplot(gs00[0, 0])
# ax01.set_yticks([0, 1, 2], minor=False)
# ax01.set_yticklabels(['NESTEROV', '', ''])
# ax01.set_xticks([0, 1, 2, 3], minor=False)
# ax01.set_xticklabels(['', 'Adam', 'Nesterov', ''])
# ax01.xaxis.tick_top()
#
# ax02 = plt.subplot(gs00[0, 1])
# ax03 = plt.subplot(gs00[1, 0])
# ax03.set_yticks([0, 1, 2], minor=False)
# ax03.set_yticklabels('')
# ax04 = plt.subplot(gs00[1, 1])
#
# # Create inner-inner layer:
# gs000 = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec=gs00[0])
# ax001 = plt.subplot(gs000[0, 0])
# ax001_bot = ax001.twiny()
# ax001.set_xticks([0, 1, 2], minor=False)
# ax001.set_xticklabels(['', '', 'ELU'])
# ax001.xaxis.tick_top()
# ax001.set_yticks([0, 1, 2], minor=False)
# ax001.set_yticklabels('')
# ax001_figure_position = ax001.get_position()
# color_box = patches.Rectangle((0, 0), 1, 1, facecolor='red')
# ax001.add_patch(color_box)
# # ax001.patch.set_facecolor('green')
# # ax001.patch.set_alpha(0.1)
# ax001_bot.set_xlim(ax001.get_xlim())
# # ax001_bot.set_xticks(ax001.get_xticks())
# ax001_bot.set_xticks([0, 1, 2, 3, 4], minor=True)
# ax001_bot.set_xticklabels(['', 'TB=10', '', 'TB=20', ''], minor=True)
# ax001_bot.set_xticklabels('', minor=False)
# ax001_bot.set_yticklabels('', minor=False)
# ax001_bot.xaxis.tick_bottom()
#
#
# ax002 = plt.subplot(gs000[0, 1])
# ax002_bot = ax002.twiny()
# ax002.set_xticks([0, 1, 2], minor=False)
# ax002.set_xticklabels('', minor=False)
# ax002_bot.set_xticks([0, 1, 2], minor=False)
# ax002_bot.set_xticklabels('', minor=False)
# ax002_bot.set_yticklabels('', minor=False)

# ax003 = plt.subplot(gs000[1, 0])
# ax003.set_yticks([0, 1, 2], minor=False)
# ax003.set_yticklabels(['NESTEROV', '', ''])


# ax1 = plt.subplot(gs[2, 0])
# # Hide major tick labels:
# ax1.set_xticks(np.arange(0, num_unique_initializers+1, 1), minor=False)
# ax1.set_xticklabels('', minor=False)
#
# # Customize minor tick labels:
# ax1.set_xticks(np.arange(0, num_unique_initializers, 0.5), minor=True)
# ax1.set_xticklabels(np.arange(0, num_unique_initializers, 0.5), minor=True)
# ax1.set_xticklabels(['', 'HE_NORMAL', '', 'HE_UNIFORM', '', 'NORM_TRUNC', ''], minor=True)
# ax1.xaxis.tick_bottom()



# ax1.xaxis.tick_top()
# ax1 = plt.subplot(gs[0, 0])
# ax2 = plt.subplot(gs[0, 1])
# ax2.yaxis.tick_right()
#
# ax3 = plt.subplot(gs[1, 0])
# ax4 = plt.subplot(gs[1, 1])
# ax4.yaxis.tick_right()
# ax = plt.subplot2grid((2, 2), (0, 0))

# plt.subplots_adjust(wspace=0, hspace=0)
# plt.show()

